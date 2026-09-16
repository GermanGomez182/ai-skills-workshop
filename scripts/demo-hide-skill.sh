#!/usr/bin/env bash
# Removes the LIVE, discoverable copy of the Skill from
# .claude/skills/ (untracked, gitignored -- see skill-source/ for
# the version-controlled master). This is a plain rm: nothing
# shows up in `git status`, so there's nothing for an agent to
# notice and "helpfully" restore from git history mid-demo.
# Used before [02] (without-skill demo) and before [06]
# (build-along). Pair with demo-restore-skill.sh.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/.claude/skills/garmin-weekly-performance-report"

if [ ! -d "$SKILL_DIR" ]; then
  echo "[!!] nothing to hide, $SKILL_DIR does not exist" >&2
  exit 1
fi

rm -rf "$SKILL_DIR"
echo "[ok] removed: $SKILL_DIR"
echo "$ ls .claude/skills/"
ls "$ROOT_DIR/.claude/skills" 2>/dev/null || echo "(empty)"
echo
echo "If you ask the agent to invoke the skill and it says 'Unknown"
echo "skill', that's expected. Discovery timing is inconsistent --"
echo "retry once or twice; if it still won't go, restart Claude Code"
echo "in this directory."
