#!/usr/bin/env bash
# Installs a version of the Skill into the demo project, replacing
# whatever is installed there now:
#   install-skill.sh v1   the small one typed live in [04]
#                         (safety net if typing goes wrong)
#   install-skill.sh v2   the full Skill for [07]
# Restart Claude afterwards so it loads the new version.
#
# Output is shown on the shared screen: keep it short and relative.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/install-skill.sh v1|v2" >&2
  return 1
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-}"
SKILL_REL=".claude/skills/garmin-weekly-performance-report"

if [[ "$VERSION" != v1 && "$VERSION" != v2 ]]; then
  echo "[!!] usage: install-skill.sh v1|v2 (got: ${VERSION:-nothing})" >&2
  exit 1
fi

rm -rf "${ROOT_DIR:?}/demo/$SKILL_REL"
mkdir -p "$ROOT_DIR/demo/.claude/skills"
cp -r "$ROOT_DIR/skill-source/$VERSION/garmin-weekly-performance-report" "$ROOT_DIR/demo/$SKILL_REL"
find "$ROOT_DIR/demo/$SKILL_REL" -name __pycache__ -type d -prune -exec rm -rf {} +
echo "[ok] installed $VERSION: $SKILL_REL"
echo "     restart Claude to load it"
