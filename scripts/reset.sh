#!/usr/bin/env bash
# Back to the starting line in demo/: no Skill installed, no report
# left in demo/output/ from a previous run. Safe to run any number
# of times. The installed Skill is not tracked by git, so this never
# shows up in `git status`.
#
# Output is shown on the shared screen: keep it short and relative.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/reset.sh" >&2
  return 1
fi

set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../demo" && pwd)"

rm -rf "${DEMO_DIR:?}/.claude/skills"
rmdir "$DEMO_DIR/.claude" 2>/dev/null || true
find "$DEMO_DIR/output" -mindepth 1 -not -name .gitkeep -delete
echo "[ok] no skills installed, output/ is empty"
