#!/usr/bin/env bash
# Presenter helper: not a substitute for the live demo, just a
# sanity check + cheat sheet. Run this before the talk, or on your
# notes monitor -- not on the screen you're sharing.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/skills/garmin-weekly-performance-report"

echo "=== AI Skills Workshop: demo check ==="
echo

if [ -d "$SKILL_DIR" ]; then
  echo "[ok] skill found: $SKILL_DIR"
else
  echo "[!!] skill not found at $SKILL_DIR -- did you delete it for the demo?"
fi

echo
echo "$ ls skills/"
ls "$ROOT_DIR/skills"
echo

echo "--- demo prompt (use it identically before and after installing the skill) ---"
echo
echo "  Create a report about my last week."
echo
echo "--- other prompts the skill should also catch ---"
echo
echo '  "Create my weekly Garmin report."'
echo '  "How did I perform last week?"'
echo '  "Give me my training and recovery summary."'
echo '  "Generate my weekly health and training report."'
echo

echo "Reminder of the beats:"
echo "  1. Run the prompt with no skill installed (or the skill dir renamed)."
echo "  2. Walk through WORKSHOP.md [03] -- MCP vs Skill."
echo "  3. Restore/build the skill. Run the exact same prompt again."
echo "  4. Narrate the comparison out loud (see NOTES.md [04])."
echo "     Write it down in demo/comparison.md afterward, not during."
echo
echo "To rehearse the offline report pipeline instead of the live agent:"
echo "  ./scripts/generate-sample-report.sh"
