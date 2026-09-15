---
name: garmin-weekly-performance-report
description: Turn Garmin Connect data (activities, sleep, HRV, resting HR, stress, body battery, training readiness) into a repeatable weekly training and recovery report. Use when the user asks to create a weekly Garmin report, a training/recovery summary, "how did I perform last week", or a weekly health and training report.
---

# Garmin Weekly Performance Report

## The job

Turn raw Garmin data into one repeatable weekly report:
training, recovery, sleep, notable changes, 4-week context.

Same structure every time. Same rules every time.
That is the entire point of this file existing.

## When this Skill applies

Trigger on requests like:

- "Create my weekly Garmin report."
- "How did I perform last week?"
- "Give me my training and recovery summary."
- "Generate my weekly health and training report."
- "Create a report about my last week."

If the user asks for something narrower (just sleep, just one
activity, a single metric), don't force the full report shape.
Answer the narrower question instead.

## Period

- Analyze the **previous 7 complete days** (Monday-Sunday), not
  including today, unless the user names a different range.
- Comparison windows:
  - current week vs previous week
  - current week vs 4-week baseline (the 4 weeks ending with the
    current week, current week included)
- If fewer than 4 weeks of data exist, say so and compare with
  whatever range is actually available. Do not pad or estimate.

## Data to retrieve

Pull these where the data source has them:

- activities (type, duration, count, distribution across the week)
- training load
- resting heart rate
- average heart rate (only where it's meaningful, e.g. per activity,
  not as a daily aggregate that mixes rest and exertion)
- HRV
- sleep duration
- sleep score
- stress
- body battery
- training readiness / recovery indicators

**Do not fabricate a missing metric.** If Garmin has no HRV data for
the period, the report says HRV data is not available for this
period. It does not estimate, interpolate, or carry over a number
from a different week.

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

## Boundaries — what this Skill does not do

- No medical diagnoses. Ever.
- No inferring injury, illness, or overtraining as fact.
- No causality from correlation. Two things happening in the same
  week is not one causing the other.
- No filling gaps with plausible-sounding numbers.
- No changing the report structure because the data is boring or
  exciting this week. The shape stays the same; the content changes.

Full language rules live in `interpretation-guidelines.md`.

## Files in this Skill

- `metrics.md` — what each metric means, how comparisons are
  computed, what counts as "meaningful."
- `report-template.md` — the exact section structure to fill in.
- `interpretation-guidelines.md` — DATA / OBSERVATION /
  INTERPRETATION rules and banned phrases.
- `scripts/generate_charts.py` — chart generation.
- `scripts/generate_pdf.py` — PDF assembly.

Read `metrics.md` and `report-template.md` before generating a
report for the first time in a session. You don't need to re-read
this file's neighbors on every single run once you know the job —
that's what progressive disclosure is for.
