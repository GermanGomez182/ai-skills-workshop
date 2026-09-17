#!/usr/bin/env bash
# Presenter pre-flight: checks the demo project is at the starting
# line and prints the beats. Run it before the talk, on your notes
# monitor -- not on the screen you're sharing.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/run-demo.sh" >&2
  return 1
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/demo"

echo "=== AI Skills Workshop: pre-flight ==="
echo

if [ -d "$DEMO_DIR/.claude/skills/garmin-weekly-performance-report" ]; then
  echo "[!!] a skill is installed in demo/ -- run scripts/demo-reset.sh before [02]"
else
  echo "[ok] no skill installed in demo/"
fi

if [ -n "$(find "$DEMO_DIR/output" -mindepth 1 -not -name .gitkeep -print -quit)" ]; then
  echo "[!!] demo/output/ has files from a previous run -- run scripts/demo-reset.sh"
else
  echo "[ok] demo/output/ is empty"
fi

if [ -d "$HOME/.garminconnect" ]; then
  echo "[ok] Garmin tokens found in ~/.garminconnect"
else
  echo "[!!] no Garmin tokens in ~/.garminconnect -- the MCP server won't connect"
fi

cat <<'BEATS'

The prompt, identical all three times:

  Create a report about my last week.

The beats (terminal inside demo/):

  [02] ../scripts/demo-reset.sh
       ../scripts/claude-demo.sh             run the prompt -> no skill
  [04] type the v1 SKILL.md                  (safety net: ../scripts/install-skill.sh v1)
       exit, ../scripts/claude-demo.sh       run the prompt -> small table
  [05] "Create a report about my last 3 days."
  [07] ../scripts/install-skill.sh v2
       exit, ../scripts/claude-demo.sh       run the prompt -> web report opens

Offline fallback (no Garmin): ../scripts/generate-sample-report.sh
BEATS
