#!/usr/bin/env bash
# Deploys the version-controlled master (skill-source/) into the
# LIVE, discoverable location (.claude/skills/, untracked). Safe to
# run as a fallback mid-[06] if a live rebuild goes sideways --
# restoring gets you back to a working Skill for [07] even if the
# build-along didn't finish.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skill-source/garmin-weekly-performance-report"
SKILL_DIR="$ROOT_DIR/.claude/skills/garmin-weekly-performance-report"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "[!!] no master copy found at $SOURCE_DIR" >&2
  exit 1
fi

if [ -d "$SKILL_DIR" ]; then
  echo "[!!] $SKILL_DIR already exists -- remove it first" >&2
  echo "     (if this is a live-built version you want to keep, move" >&2
  echo "     it aside instead of overwriting it)" >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/.claude/skills"
cp -r "$SOURCE_DIR" "$SKILL_DIR"
echo "[ok] deployed: $SOURCE_DIR -> $SKILL_DIR"
echo "$ ls .claude/skills/"
ls "$ROOT_DIR/.claude/skills"
echo
echo "If the agent says 'Unknown skill' when you invoke it, retry"
echo "once or twice before restarting Claude Code -- discovery"
echo "timing has been inconsistent in testing."
