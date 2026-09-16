#!/usr/bin/env bash
# Moves the real garmin-weekly-performance-report Skill out of
# .claude/skills/ -- the actual directory Claude Code scans for
# project-level Skills -- so it's genuinely not installed.
# Used twice in the talk: before [02] (without-skill demo) and
# before [06] (build-along). Pair with demo-restore-skill.sh.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/.claude/skills/garmin-weekly-performance-report"
BACKUP_DIR="$ROOT_DIR/.demo-backup/garmin-weekly-performance-report"

if [ -d "$BACKUP_DIR" ]; then
  echo "[!!] backup already exists at $BACKUP_DIR -- already hidden?" >&2
  echo "     run scripts/demo-restore-skill.sh first if that's wrong." >&2
  exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
  echo "[!!] nothing to hide, $SKILL_DIR does not exist" >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/.demo-backup"
mv "$SKILL_DIR" "$BACKUP_DIR"
echo "[ok] hidden: $SKILL_DIR -> $BACKUP_DIR"
echo "$ ls .claude/skills/"
ls "$ROOT_DIR/.claude/skills" 2>/dev/null || echo "(empty)"
echo
echo "Now restart Claude Code in this directory before running the"
echo "demo prompt. Skills are discovered at session start, not"
echo "hot-reloaded mid-session -- a session already running will"
echo "still think this Skill exists until it's restarted."
