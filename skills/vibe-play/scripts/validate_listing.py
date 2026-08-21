#!/usr/bin/env python3
"""Validate a fastlane supply Android metadata tree.

No network. Exit 0 on success, 1 on any hard failure.

Usage:
  python3 validate_listing.py [metadata_android_dir]
  python3 validate_listing.py fastlane/metadata/android
  python3 validate_listing.py --feature-graphic path/to/featureGraphic.png

If no directory is given, looks for ./fastlane/metadata/android, then ./ .
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

TITLE_LIMIT = 30
SHORT_LIMIT = 80
FULL_LIMIT = 4000

REQUIRED = ("title.txt", "short_description.txt", "full_description.txt")
OPTIONAL = ("video.txt",)

WORD_SOUP = re.compile(
    r"(?m)^(?:\s*[-*]?\s*)?(?:[\w][\w \-]{0,40}\s*,\s*){6,}[\w][\w \-]{0,40}\s*\.?$"
)
PROMO = re.compile(
    r"(?i)\b(#1|best of play|app of the year|million downloads|10% off|"
    r"cash back|free for a limited|download now|install now|try now|play now)\b"
)
EMOJI = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U00002700-\U000027bf"
    "\U0001f000-\U0001f02f"
    "]+"
)


class Result:
    def __init__(self) -> None:
        self.hard: list[str] = []
        self.warn: list[str] = []
        self.ok: list[str] = []

    def fail(self, msg: str) -> None:
        self.hard.append(msg)
        print(f" FAIL  {msg}")

    def warn_(self, msg: str) -> None:
        self.warn.append(msg)
        print(f" WARN  {msg}")

    def pass_(self, msg: str) -> None:
        self.ok.append(msg)
        print(f" PASS  {msg}")


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    # Play / fastlane treat these as single-line fields; keep interior
    # newlines for full_description but strip one trailing newline.
    if path.name != "full_description.txt":
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if text.endswith("\n"):
            text = text[:-1]
        return text
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def png_info(path: Path) -> tuple[int, int, int, bool] | None:
    """Return (width, height, color_type, has_alpha) or None if not PNG."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    # IHDR is the first chunk
    if data[12:16] != b"IHDR":
        return None
    width, height, _bit, color_type = struct.unpack(">IIBB", data[16:26])
    has_alpha = color_type in (4, 6)  # grayscale+alpha or RGBA
    # tRNS chunk also counts as alpha
    if b"tRNS" in data:
        has_alpha = True
    return width, height, color_type, has_alpha


def jpeg_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 1:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        if i + 1 >= len(data):
            break
        seglen = struct.unpack(">H", data[i : i + 2])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3):
            if i + 6 < len(data):
                height, width = struct.unpack(">HH", data[i + 3 : i + 7])
                return width, height
            return None
        i += seglen
    return None


def image_size(path: Path) -> tuple[int, int] | None:
    info = png_info(path)
    if info:
        return info[0], info[1]
    return jpeg_size(path)


def find_metadata_root(arg: Path | None) -> Path:
    if arg is not None:
        p = arg.expanduser().resolve()
        if not p.exists():
            raise SystemExit(f" FAIL  path does not exist: {p}")
        if p.is_file():
            raise SystemExit(f" FAIL  expected a directory, got a file: {p}")
        # Accept either the android/ dir or a single locale dir
        return p
    cwd = Path.cwd()
    for cand in (
        cwd / "fastlane" / "metadata" / "android",
        cwd / "metadata" / "android",
        cwd,
    ):
        if cand.is_dir() and (
            any((cand / n).is_file() for n in REQUIRED)
            or any((d / "title.txt").is_file() for d in cand.iterdir() if d.is_dir())
        ):
            return cand
    raise SystemExit(
        " FAIL  no fastlane/metadata/android tree found. "
        "Pass the directory: python3 validate_listing.py fastlane/metadata/android"
    )


def locale_dirs(root: Path) -> list[Path]:
    if (root / "title.txt").is_file():
        return [root]
    dirs = sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "images"
    )
    return dirs


def check_locale(loc: Path, r: Result) -> None:
    label = loc.name
    missing = [name for name in REQUIRED if not (loc / name).is_file()]
    if missing:
        r.fail(f"{label}: missing required file(s): {', '.join(missing)}")
        return

    fields = {
        "title.txt": TITLE_LIMIT,
        "short_description.txt": SHORT_LIMIT,
        "full_description.txt": FULL_LIMIT,
    }
    texts: dict[str, str] = {}
    for name, limit in fields.items():
        path = loc / name
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            r.fail(f"{label}/{name}: not valid UTF-8")
            continue
        texts[name] = text
        n = len(text)
        shown = f"{name.removesuffix('.txt')} ({n}/{limit})"
        if n == 0:
            r.fail(f"{label}: {shown} is empty")
        elif n > limit:
            r.fail(f"{label}: {shown} exceeds hard limit {limit}")
        else:
            r.pass_(f"{label}: {shown}")

    title = texts.get("title.txt", "")
    short = texts.get("short_description.txt", "")
    full = texts.get("full_description.txt", "")

    if title and title == title.upper() and any(c.isalpha() for c in title):
        r.warn_(f"{label}: title is ALL CAPS — only ok if that is the brand")
    if title and EMOJI.search(title):
        r.fail(f"{label}: title contains emoji/emoticon (Metadata policy)")
    if short and EMOJI.search(short):
        r.warn_(f"{label}: short description contains emoji — Play asks you not to")
    if title and PROMO.search(title):
        r.fail(f"{label}: title contains ranking/price/promo language")
    if short and PROMO.search(short):
        r.fail(f"{label}: short description contains ranking/price/promo/CTA language")
    if full and PROMO.search(full):
        r.fail(f"{label}: full description contains ranking/price/promo/CTA language")
    if short and full and full.lstrip().startswith(short.strip()):
        r.fail(
            f"{label}: full description opens by repeating the short description "
            "(Play best practices: don't)"
        )
    if full and WORD_SOUP.search(full):
        r.fail(
            f"{label}: full description looks like a comma-separated keyword block "
            "(Metadata policy violation)"
        )
    if short and WORD_SOUP.search(short):
        r.fail(f"{label}: short description looks like a keyword list")

    video = loc / "video.txt"
    if video.is_file():
        url = read_text(video).strip()
        if url:
            if "youtube.com" not in url and "youtu.be" not in url:
                r.warn_(f"{label}: video.txt is not a YouTube URL — verify in Play Console")
            if "?" in url and "listing=" not in url:
                # Play asks for no extra params (timecodes, etc.)
                r.warn_(f"{label}: video.txt has query params — Play wants a bare YouTube URL")


def check_feature_graphic(path: Path, r: Result) -> None:
    if not path.is_file():
        r.fail(f"feature graphic not found: {path}")
        return
    png = png_info(path)
    if png:
        w, h, color_type, has_alpha = png
        shown = f"{path} ({w}×{h})"
        if (w, h) != (1024, 500):
            r.fail(f"feature graphic {shown} must be 1024×500")
        else:
            r.pass_(f"feature graphic {shown}")
        if has_alpha or color_type in (4, 6):
            r.fail(
                f"feature graphic {path} has an alpha channel — Play wants JPEG or 24-bit PNG, no alpha"
            )
        return
    jpeg = jpeg_size(path)
    if jpeg:
        w, h = jpeg
        shown = f"{path} ({w}×{h})"
        if (w, h) != (1024, 500):
            r.fail(f"feature graphic {shown} must be 1024×500")
        else:
            r.pass_(f"feature graphic {shown} JPEG")
        return
    r.fail(f"feature graphic {path} is not a PNG or JPEG")


def check_icon(path: Path, r: Result) -> None:
    if not path.is_file():
        r.fail(f"icon not found: {path}")
        return
    png = png_info(path)
    if not png:
        r.fail(f"icon {path} must be a 32-bit PNG (512×512)")
        return
    w, h, _ct, _alpha = png
    shown = f"{path} ({w}×{h})"
    if (w, h) != (512, 512):
        r.fail(f"icon {shown} must be 512×512")
    else:
        r.pass_(f"icon {shown}")


def discover_graphics(root: Path) -> list[Path]:
    found: list[Path] = []
    for pattern in (
        "**/images/featureGraphic.png",
        "**/images/featureGraphic.jpg",
        "**/images/featureGraphic.jpeg",
    ):
        found.extend(root.glob(pattern))
    return found


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "metadata_dir",
        nargs="?",
        type=Path,
        help="fastlane/metadata/android (or a single locale dir)",
    )
    p.add_argument(
        "--feature-graphic",
        type=Path,
        action="append",
        default=[],
        help="path to a feature graphic to dimension-check (repeatable)",
    )
    p.add_argument(
        "--icon",
        type=Path,
        action="append",
        default=[],
        help="path to a 512×512 icon to dimension-check (repeatable)",
    )
    args = p.parse_args(argv)

    r = Result()
    try:
        root = find_metadata_root(args.metadata_dir)
    except SystemExit as e:
        print(e)
        return 1

    print(f"vibe-play validate  {root}")
    print()

    locales = locale_dirs(root)
    if not locales:
        r.fail(f"no locale directories (and no title.txt) under {root}")
    for loc in locales:
        check_locale(loc, r)

    graphics = list(args.feature_graphic)
    if not graphics:
        graphics = discover_graphics(root)
    for g in graphics:
        check_feature_graphic(g.expanduser(), r)

    for ic in args.icon:
        check_icon(ic.expanduser(), r)

    print()
    if r.hard:
        print(f"{len(r.hard)} FAIL  {len(r.warn)} WARN  {len(r.ok)} PASS")
        print("listing is not shippable until every FAIL is fixed")
        return 1
    print(f"0 FAIL  {len(r.warn)} WARN  {len(r.ok)} PASS")
    print("listing OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
