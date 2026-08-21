#!/usr/bin/env python3
"""Thin Play Developer API v3 client for vibe-play.

Only the official Publishing API "edits" resources used by this skill, plus
the documented applications.dataSafety write. No invented paths.

Docs:
  https://developers.google.com/android-publisher/edits
  https://developers.google.com/android-publisher/api-ref/rest/v3/edits.listings
  https://developers.google.com/android-publisher/api-ref/rest/v3/edits.images
  https://developers.google.com/android-publisher/api-ref/rest/v3/edits.details
  https://developers.google.com/android-publisher/api-ref/rest/v3/AppImageType
  https://developers.google.com/android-publisher/api-ref/rest/v3/applications/dataSafety

Auth: a Google Cloud service-account JSON with Play Console access, stored
at ~/.vibe-play/play-sa.json (never in a repo). Scope:
  https://www.googleapis.com/auth/androidpublisher

This script will not:
  - create custom store listings (no public API)
  - start experiments (no public API)
  - fill content rating / target audience / ads / app access / news /
    government / financial / health / photo-permission forms
  - invent AppImageType values (promoGraphic is NOT in the enum)

Requires: python3 and, for live calls, google-auth + google-api-python-client
  python3 -m pip install google-auth google-auth-httplib2 google-api-python-client
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HOST = "https://androidpublisher.googleapis.com"
SCOPE = "https://www.googleapis.com/auth/androidpublisher"
API_NAME = "androidpublisher"
API_VERSION = "v3"

# Official AppImageType enum values. Do not add to this list.
APP_IMAGE_TYPES = (
    "phoneScreenshots",
    "sevenInchScreenshots",
    "tenInchScreenshots",
    "tvScreenshots",
    "wearScreenshots",
    "icon",
    "featureGraphic",
    "tvBanner",
)

CFG_DIR = Path.home() / ".vibe-play"
DEFAULT_SA = CFG_DIR / "play-sa.json"
DEFAULT_CFG = CFG_DIR / "config.json"


def _die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_config() -> dict:
    if not DEFAULT_CFG.is_file():
        return {}
    try:
        return json.loads(DEFAULT_CFG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _die(f"unreadable config: {DEFAULT_CFG}")
    return {}


def resolve_sa(cli_path: str | None) -> Path:
    cfg = load_config()
    raw = (
        cli_path
        or os.environ.get("PLAY_SA")
        or (cfg.get("play") or {}).get("service_account_path")
        or str(DEFAULT_SA)
    )
    path = Path(os.path.expanduser(raw))
    if not path.is_file():
        _die(
            f"no service-account JSON at {path}\n"
            f"fix: store the Play Developer API key at {DEFAULT_SA} && chmod 600 {DEFAULT_SA}\n"
            "or pass --sa /path/to.json. Console-manual path: skip this script."
        )
    return path


def resolve_package(cli_pkg: str | None) -> str:
    cfg = load_config()
    pkg = cli_pkg or os.environ.get("PLAY_PACKAGE") or (cfg.get("play") or {}).get(
        "package_name"
    )
    if not pkg:
        _die(
            "no package name. Set play.package_name in ~/.vibe-play/config.json "
            "or pass --package com.example.glowup"
        )
    return pkg


def build_service(sa_path: Path):
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("MISSING_DEPS")
        _die(
            "missing Google auth libraries.\n"
            "fix: python3 -m pip install google-auth google-auth-httplib2 google-api-python-client",
            2,
        )
    creds = service_account.Credentials.from_service_account_file(
        str(sa_path), scopes=[SCOPE]
    )
    return build(API_NAME, API_VERSION, credentials=creds, cache_discovery=False)


def cmd_ping(args: argparse.Namespace) -> int:
    """Mint an access token. No Play write. Proves the JSON is a service account
    that Google will exchange. Does not prove Play Console ACL.
    """
    sa = resolve_sa(args.sa)
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        print("MISSING_DEPS")
        if args.quiet:
            return 2
        _die(
            "missing Google auth libraries.\n"
            "fix: python3 -m pip install google-auth google-auth-httplib2 google-api-python-client",
            2,
        )
    creds = service_account.Credentials.from_service_account_file(
        str(sa), scopes=[SCOPE]
    )
    creds.refresh(Request())
    if not creds.token:
        _die("token mint failed")
    print("OK")
    if not args.quiet:
        print("token minted; no Play resource was read or written")
        print(f"scope {SCOPE}")
    return 0


def _insert_edit(service, package: str) -> str:
    """POST /androidpublisher/v3/applications/{{packageName}}/edits"""
    body = service.edits().insert(packageName=package, body={}).execute()
    return body["id"]


def _delete_edit(service, package: str, edit_id: str) -> None:
    """DELETE /androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}"""
    service.edits().delete(packageName=package, editId=edit_id).execute()


def cmd_listings(args: argparse.Namespace) -> int:
    """GET …/edits/{{editId}}/listings  (opens a throwaway edit, then deletes it)."""
    sa = resolve_sa(args.sa)
    package = resolve_package(args.package)
    service = build_service(sa)
    edit_id = _insert_edit(service, package)
    try:
        data = (
            service.edits()
            .listings()
            .list(packageName=package, editId=edit_id)
            .execute()
        )
    finally:
        _delete_edit(service, package, edit_id)
    listings = data.get("listings") or []
    print(json.dumps(listings, indent=2, ensure_ascii=False))
    print(f"# {len(listings)} listing(s)  (read-only; edit abandoned)", file=sys.stderr)
    return 0


def cmd_listing(args: argparse.Namespace) -> int:
    """GET …/edits/{{editId}}/listings/{{language}}"""
    sa = resolve_sa(args.sa)
    package = resolve_package(args.package)
    service = build_service(sa)
    edit_id = _insert_edit(service, package)
    try:
        data = (
            service.edits()
            .listings()
            .get(packageName=package, editId=edit_id, language=args.language)
            .execute()
        )
    finally:
        _delete_edit(service, package, edit_id)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_details(args: argparse.Namespace) -> int:
    """GET …/edits/{{editId}}/details
    Fields: defaultLanguage, contactWebsite, contactEmail, contactPhone.
    Privacy policy is NOT on this resource.
    """
    sa = resolve_sa(args.sa)
    package = resolve_package(args.package)
    service = build_service(sa)
    edit_id = _insert_edit(service, package)
    try:
        data = service.edits().details().get(packageName=package, editId=edit_id).execute()
    finally:
        _delete_edit(service, package, edit_id)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_list_images(args: argparse.Namespace) -> int:
    """GET …/edits/{{editId}}/listings/{{language}}/{{imageType}}"""
    if args.image_type not in APP_IMAGE_TYPES:
        _die(
            f"unknown imageType {args.image_type!r}. Official AppImageType values:\n  "
            + "\n  ".join(APP_IMAGE_TYPES)
        )
    sa = resolve_sa(args.sa)
    package = resolve_package(args.package)
    service = build_service(sa)
    edit_id = _insert_edit(service, package)
    try:
        data = (
            service.edits()
            .images()
            .list(
                packageName=package,
                editId=edit_id,
                language=args.language,
                imageType=args.image_type,
            )
            .execute()
        )
    finally:
        _delete_edit(service, package, edit_id)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def _read_locale_files(locale_dir: Path) -> dict:
    def one(name: str) -> str:
        p = locale_dir / name
        if not p.is_file():
            return ""
        text = p.read_text(encoding="utf-8-sig")
        return text[:-1] if text.endswith("\n") else text

    return {
        "language": locale_dir.name,
        "title": one("title.txt"),
        "shortDescription": one("short_description.txt"),
        "fullDescription": one("full_description.txt"),
        "video": one("video.txt").strip(),
    }


def cmd_update_listings(args: argparse.Namespace) -> int:
    """PUT …/edits/{{editId}}/listings/{{language}} for each locale dir, then
    GET each back, then commit (or abandon with --dry-run).
    """
    root = Path(args.metadata_dir).expanduser().resolve()
    if not root.is_dir():
        _die(f"metadata dir not found: {root}")
    locales = sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and (d / "title.txt").is_file()
    )
    if not locales:
        _die(f"no locale dirs with title.txt under {root}")

    sa = resolve_sa(args.sa)
    package = resolve_package(args.package)
    service = build_service(sa)
    edit_id = _insert_edit(service, package)
    print(f"edit {edit_id} opened", file=sys.stderr)
    mismatches = 0
    try:
        for loc in locales:
            body = _read_locale_files(loc)
            service.edits().listings().update(
                packageName=package,
                editId=edit_id,
                language=body["language"],
                body=body,
            ).execute()
            got = (
                service.edits()
                .listings()
                .get(packageName=package, editId=edit_id, language=body["language"])
                .execute()
            )
            ok = True
            for field in ("title", "shortDescription", "fullDescription", "video"):
                if (got.get(field) or "") != (body.get(field) or ""):
                    print(
                        f"READBACK MISMATCH {body['language']} {field}",
                        file=sys.stderr,
                    )
                    ok = False
                    mismatches += 1
            status = "OK" if ok else "MISMATCH"
            print(
                f"{status} {body['language']}  "
                f"title ({len(body['title'])}/30)  "
                f"short ({len(body['shortDescription'])}/80)  "
                f"full ({len(body['fullDescription'])}/4000)"
            )
        if args.dry_run or mismatches:
            print("abandoning edit (dry-run or mismatch)", file=sys.stderr)
            _delete_edit(service, package, edit_id)
            return 1 if mismatches else 0
        service.edits().commit(packageName=package, editId=edit_id).execute()
        print("committed. Re-run `listings` after Play finishes propagating.")
        return 0
    except Exception:
        try:
            _delete_edit(service, package, edit_id)
        except Exception:
            pass
        raise


def cmd_docs(_: argparse.Namespace) -> int:
    print(
        """
Official Play Developer API paths vibe-play is allowed to call
==============================================================

Edits lifecycle
  POST   {host}/androidpublisher/v3/applications/{{packageName}}/edits
  GET    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}
  DELETE {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}
  POST   {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}:commit
  POST   {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}:validate

Listings  (resource fields: language, title, fullDescription, shortDescription, video)
  GET    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings
  GET    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}
  PUT    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}
  PATCH  {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}
  DELETE {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}

Details  (fields: defaultLanguage, contactWebsite, contactEmail, contactPhone)
  GET    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/details
  PATCH  {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/details
  PUT    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/details

Images  (imageType ∈ {types})
  GET    {host}/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}/{{imageType}}
  POST   {host}/upload/androidpublisher/v3/applications/{{packageName}}/edits/{{editId}}/listings/{{language}}/{{imageType}}

Data safety (write-only; empty response; verify in Console)
  POST   {host}/androidpublisher/v3/applications/{{packageName}}/dataSafety
  body   {{ "safetyLabels": "<csv contents>" }}
  csv    https://support.google.com/googleplay/android-developer/answer/10787469

NOT in the public API (Console-only — do not invent a path)
  custom store listings, store listing experiments, privacy policy URL,
  content rating, target audience, ads declaration, app access,
  news / government / financial / health / photos-videos questionnaires.

Scope: {scope}
""".format(
            host=HOST,
            types=", ".join(APP_IMAGE_TYPES),
            scope=SCOPE,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sa", help="path to service-account JSON")
    p.add_argument("--package", help="applicationId / package name")
    p.add_argument("--quiet", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="mint a token; no Play write")
    sub.add_parser("listings", help="GET all localized listings (read-only edit)")
    g = sub.add_parser("listing", help="GET one localized listing")
    g.add_argument("language", help="BCP-47 tag, e.g. en-US")
    sub.add_parser("details", help="GET edits.details (contact + defaultLanguage)")
    im = sub.add_parser("list-images", help="GET images for one language + type")
    im.add_argument("language")
    im.add_argument("image_type", choices=APP_IMAGE_TYPES)
    up = sub.add_parser(
        "update-listings",
        help="PUT each locale from a fastlane android/ tree, GET back, commit",
    )
    up.add_argument("metadata_dir")
    up.add_argument(
        "--dry-run",
        action="store_true",
        help="write into an edit and read back, then abandon (no commit)",
    )
    sub.add_parser("docs", help="print the official paths this stub will call")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    dispatch = {
        "ping": cmd_ping,
        "listings": cmd_listings,
        "listing": cmd_listing,
        "details": cmd_details,
        "list-images": cmd_list_images,
        "update-listings": cmd_update_listings,
        "docs": cmd_docs,
    }
    try:
        return dispatch[args.cmd](args)
    except SystemExit:
        raise
    except Exception as exc:
        _die(f"Play API error: {exc}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
