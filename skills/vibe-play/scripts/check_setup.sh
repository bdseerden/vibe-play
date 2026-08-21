#!/usr/bin/env bash
# Vibe Play setup check. Prints one PASS/WARN/FAIL line per prerequisite
# and a fix command for anything missing. Never prints key material.
# Invoke: bash scripts/check_setup.sh   (or chmod +x and run it)
set -uo pipefail
CFG_DIR="$HOME/.vibe-play"
CFG="$CFG_DIR/config.json"
SA="$CFG_DIR/play-sa.json"
FAILS=0
pass() { echo " PASS $1"; }
warn() { echo " WARN $1"; }
fail() { echo " FAIL $1"; FAILS=$((FAILS+1)); }
echo "vibe-play setup check"
echo
if command -v python3 >/dev/null; then
  pass "python3 present ($(python3 -c 'import sys; print("%d.%d"%sys.version_info[:2])'))"
else
  fail "python3 missing — install Python 3.9+ (sudo apt-get install python3 / brew install python)"
fi
if [ -d "$CFG_DIR" ]; then
  pass "config dir exists ($CFG_DIR)"
  dperms=$(stat -f "%Lp" "$CFG_DIR" 2>/dev/null || stat -c "%a" "$CFG_DIR" 2>/dev/null)
  [ "$dperms" = "700" ] && pass "config dir permissions 700" || warn "config dir permissions are $dperms — run: chmod 700 $CFG_DIR"
else
  fail "no config dir at $CFG_DIR — run: mkdir -p $CFG_DIR && chmod 700 $CFG_DIR"
fi
if [ -f "$CFG" ]; then
  pass "config exists ($CFG)"
  perms=$(stat -f "%Lp" "$CFG" 2>/dev/null || stat -c "%a" "$CFG" 2>/dev/null)
  [ "$perms" = "600" ] && pass "config permissions 600" || warn "config permissions are $perms — run: chmod 600 $CFG"
else
  warn "no config at $CFG — run the setup wizard (Phase 0 in SKILL.md). Console-manual path still works without it."
fi
if [ -f "$SA" ]; then
  pass "Play service-account JSON present"
  perms=$(stat -f "%Lp" "$SA" 2>/dev/null || stat -c "%a" "$SA" 2>/dev/null)
  [ "$perms" = "600" ] && pass "service-account permissions 600" || warn "service-account permissions are $perms — run: chmod 600 $SA"
else
  warn "no Play service-account JSON at $SA — API uploads are unavailable. Use Play Console by hand. See Phase 0 in SKILL.md."
fi
if command -v fastlane >/dev/null; then
  pass "fastlane present"
else
  warn "fastlane not installed — needed for metadata/image upload. Install: gem install fastlane   or   brew install fastlane. Console-manual path still works."
fi
RENDERER="$(cd "$(dirname "$0")/../renderer" 2>/dev/null && pwd)" || true
if [ -n "${RENDERER:-}" ] && [ -d "$RENDERER" ]; then
  if command -v node >/dev/null; then
    pass "node present"
  else
    warn "node missing — needed only if a renderer/ directory is present"
  fi
fi
if [ -f "$CFG" ] && command -v python3 >/dev/null; then
  python3 - "$CFG" << 'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
def g(path):
    v = cfg
    for k in path.split("."):
        v = v.get(k) if isinstance(v, dict) else None
    return v or ""
pkg = g("play.package_name")
print(" PASS package name set (%s)" % pkg if pkg else " WARN no play.package_name in config — set it before any API call")
eng = g("translation.engine")
if eng == "subagents":
    print(" PASS translation engine: Claude subagents (no external API needed)")
elif eng in ("deepseek", "openai"):
    print(" PASS translation engine: %s" % eng)
elif eng:
    print(" WARN unknown translation engine %r — expected subagents | deepseek | openai" % eng)
else:
    print(" WARN no translation.engine in config — defaulting to subagents")
src = g("keyword_source")
if src in ("astro", "manual"):
    print(" PASS keyword source: %s" % src)
elif src == "none":
    print(" WARN keyword source: none — phase 1 runs in honest degraded mode")
elif src:
    print(" PASS keyword source: %s (Play-capable ASO tool; user pastes numbers)" % src)
else:
    print(" WARN no keyword_source in config — phase 1 will ask")
PY
fi
echo
if [ "$FAILS" -eq 0 ]; then
  echo "setup OK"
  exit 0
fi
echo "$FAILS check(s) failed — fix the FAIL lines above before running the pipeline"
exit 1
