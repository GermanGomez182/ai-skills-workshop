#!/usr/bin/env bash
# Runs the Skill's own scripts against the synthetic sample data,
# entirely offline. Useful for rehearsing the PDF/chart output
# before the talk, or as a fallback if Garmin MCP is unreachable.
#
# The narrative text this produces is a rule-based approximation,
# not the model's actual interpretation -- see the docstring in
# generate_pdf.py. The live demo, with the agent actually reading
# interpretation-guidelines.md, is the real thing.
# Sourcing (". ./scripts/offline-report.sh") would run `set -e` and `exit`
# inside your own shell and close the terminal/tmux pane. Refuse.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/offline-report.sh" >&2
  return 1
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Runs straight from the version-controlled master -- this is a
# plain script invocation, not a Claude Code skill-discovery path,
# so it doesn't need the deployed .claude/skills/ copy to exist.
SKILL_DIR="$ROOT_DIR/skill-source/v2/garmin-weekly-performance-report"
DATA_FILE="$ROOT_DIR/sample-data/sample-garmin-week.json"
OUT_DIR="$ROOT_DIR/demo/output"
CHARTS_DIR="$OUT_DIR/charts"

if [ -d "$ROOT_DIR/.venv" ]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$OUT_DIR"

echo "building web report..."
python3 "$SKILL_DIR/scripts/generate_html.py" \
  --input "$DATA_FILE" \
  --output "$OUT_DIR/weekly-report.html" >/dev/null

echo "generating charts..."
python3 "$SKILL_DIR/scripts/generate_charts.py" \
  --input "$DATA_FILE" \
  --output-dir "$CHARTS_DIR" >/dev/null

echo "assembling pdf..."
python3 "$SKILL_DIR/scripts/generate_pdf.py" \
  --input "$DATA_FILE" \
  --charts-dir "$CHARTS_DIR" \
  --output "$OUT_DIR/weekly-report.pdf" >/dev/null

echo "done: output/weekly-report.html, output/weekly-report.pdf"
cd "$ROOT_DIR/demo" && "$SKILL_DIR/scripts/open_in_chrome.sh" output/weekly-report.html
