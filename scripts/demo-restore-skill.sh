#!/usr/bin/env bash
# Restores the Skill hidden by demo-hide-skill.sh. Safe to run as
# a fallback mid-[06] if a live rebuild goes sideways -- restoring
# gets you back to a working Skill for [07] even if the build-along
# didn't finish.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/.claude/skills/garmin-weekly-performance-report"
BACKUP_DIR="$ROOT_DIR/.demo-backup/garmin-weekly-performance-report"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "[!!] no backup found at $BACKUP_DIR -- nothing to restore" >&2
  exit 1
fi

if [ -d "$SKILL_DIR" ]; then
  echo "[!!] $SKILL_DIR already exists -- remove or rename it first" >&2
  echo "     (if this is a live-built version you want to keep, move" >&2
  echo "     it aside instead of overwriting it)" >&2
  exit 1
fi

mv "$BACKUP_DIR" "$SKILL_DIR"
rmdir "$ROOT_DIR/.demo-backup" 2>/dev/null || true
echo "[ok] restored: $SKILL_DIR"
echo "$ ls .claude/skills/"
ls "$ROOT_DIR/.claude/skills"
echo
echo "Now restart Claude Code in this directory -- Skills are"
echo "discovered at session start, not picked up mid-session."
