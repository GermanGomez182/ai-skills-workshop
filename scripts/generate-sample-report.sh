#!/usr/bin/env bash
# Runs the Skill's own scripts against the synthetic sample data,
# entirely offline. Useful for rehearsing the PDF/chart output
# before the talk, or as a fallback if Garmin MCP is unreachable.
#
# The narrative text this produces is a rule-based approximation,
# not the model's actual interpretation -- see the docstring in
# generate_pdf.py. The live demo, with the agent actually reading
# interpretation-guidelines.md, is the real thing.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT_DIR/skills/garmin-weekly-performance-report"
DATA_FILE="$ROOT_DIR/sample-data/sample-garmin-week.json"
OUT_DIR="$ROOT_DIR/output"
CHARTS_DIR="$OUT_DIR/charts"

if [ -d "$ROOT_DIR/.venv" ]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$OUT_DIR"

echo "generating charts..."
python3 "$SKILL_DIR/scripts/generate_charts.py" \
  --input "$DATA_FILE" \
  --output-dir "$CHARTS_DIR"

echo "assembling pdf..."
python3 "$SKILL_DIR/scripts/generate_pdf.py" \
  --input "$DATA_FILE" \
  --charts-dir "$CHARTS_DIR" \
  --output "$OUT_DIR/weekly-report.pdf"

echo "done: $OUT_DIR/weekly-report.pdf"
