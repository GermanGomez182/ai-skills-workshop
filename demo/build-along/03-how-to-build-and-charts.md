## How to build the report

1. Retrieve current week, previous week, and 4-week baseline data.
2. Compute per-section aggregates (see `metrics.md` for exact
   definitions and what counts as a meaningful change).
3. Classify every claim as DATA, OBSERVATION, or INTERPRETATION.
   Read `interpretation-guidelines.md` before writing a single
   sentence of prose. This is the part people get wrong.
4. Fill the structure in `report-template.md`. Don't reorder
   sections, don't invent new ones.
5. If the user wants a PDF, run
   `scripts/generate_charts.py` then `scripts/generate_pdf.py`
   (see below).

## Charts (optional, only if a PDF or images are requested)

`scripts/generate_charts.py` takes a Garmin-shaped JSON payload and
writes PNGs for:

- training duration by day
- sleep duration by day
- resting HR trend
- HRV trend
- training load vs recovery

`scripts/generate_pdf.py` lays those charts and the report content
into a single minimal, grayscale PDF. See that script's docstring
for the exact input shape it expects.

Run them from the repo root (paths below are relative to it, not
to this Skill's own directory):

```
$ python3 skills/garmin-weekly-performance-report/scripts/generate_charts.py \
    --input week.json --output-dir output/charts/
$ python3 skills/garmin-weekly-performance-report/scripts/generate_pdf.py \
    --input week.json --charts-dir output/charts/ --output output/report.pdf
```
