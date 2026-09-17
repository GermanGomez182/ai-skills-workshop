#!/usr/bin/env bash
# Presenter pre-flight: checks the demo project is at the starting
# line and prints the beats. Run it before the talk, on your notes
# monitor -- not on the screen you're sharing.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/preflight.sh" >&2
  return 1
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/demo"

echo "=== AI Skills Workshop: pre-flight ==="
echo

if [ -d "$DEMO_DIR/.claude/skills/garmin-weekly-performance-report" ]; then
  echo "[!!] a skill is installed in demo/ -- run scripts/reset.sh before [02]"
else
  echo "[ok] no skill installed in demo/"
fi

if [ -n "$(find "$DEMO_DIR/output" -mindepth 1 -not -name .gitkeep -print -quit)" ]; then
  echo "[!!] demo/output/ has files from a previous run -- run scripts/reset.sh"
else
  echo "[ok] demo/output/ is empty"
fi

if [ -d "$HOME/.garminconnect" ]; then
  echo "[ok] Garmin tokens found in ~/.garminconnect"
else
  echo "[!!] no Garmin tokens in ~/.garminconnect -- the MCP server won't connect"
fi

# Start the MCP server once so uv and the Garmin login are warm: from
# cold it has taken longer than Claude Code waits, and the first run
# of the talk then fails with CONNECT_TIMEOUT.
echo -n "[..] warming up the Garmin MCP server (up to 90s)... "
WARMUP="$(GARMIN_ENABLED_TOOLS=get_user_profile \
  GARMINTOKENS="$HOME/.garminconnect" \
  UV_CACHE_DIR=/tmp/uv-cache \
  timeout 90 uv --directory "$HOME/lab/garmin_mcp" run --locked garmin-mcp </dev/null 2>&1 || true)"

case "$WARMUP" in
  *"client initialized successfully"*) echo "ok" ;;
  *) echo "FAILED -- re-auth or check ~/lab/garmin_mcp before the talk"
     echo "$WARMUP" | tail -3 ;;
esac

cat <<'BEATS'

The prompt, identical all three times:

  Create a report about my last week.

The beats (terminal inside demo/):

  [02] ../scripts/reset.sh
       ../scripts/claude.sh             run the prompt -> no skill
  [04] type the v1 SKILL.md                  (safety net: ../scripts/install-skill.sh v1)
       exit, ../scripts/claude.sh       run the prompt -> small table
  [05] "Create a report about my last 3 days."
  [07] ../scripts/install-skill.sh v2
       exit, ../scripts/claude.sh       run the prompt -> web report opens

Offline fallback (no Garmin): ../scripts/offline-report.sh
BEATS
