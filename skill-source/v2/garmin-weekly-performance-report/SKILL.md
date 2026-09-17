---
name: garmin-weekly-performance-report
description: Turn Garmin Connect data (activities, sleep, HRV, resting HR, stress, body battery, training readiness) into a repeatable weekly training and recovery report. Use when the user asks to create a weekly Garmin report, a training/recovery summary, "how did I perform last week", or a weekly health and training report.
---

# Garmin Weekly Performance Report

## The job

Turn raw Garmin data into one repeatable weekly report:
training, recovery, sleep, notable days, Garmin baselines.

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

- Analyze the **last complete Monday-Sunday week** before today,
  unless the user names a different range.
- Work the dates out from today's date, which you already know.
  Don't run commands or scripts for date math.
- **7 days. Nothing older.** Do not fetch the previous week or a
  4-week history: every extra day is 3 more MCP calls.
- Context comes from the baselines Garmin already calculates and
  returns for each of those 7 days (7-day avg resting HR, weekly
  avg HRV, acute load). See `metrics.md`.

## Data to retrieve

Exactly these calls, nothing else. Make all of them in parallel,
in one batch:

| Call | Count | Gives you |
|---|---|---|
| `get_activities_by_date(start, end)` | 1 | type and duration of every activity |
| `get_sleep_summary(date)` | 7 | sleep duration, sleep score, overnight HRV |
| `get_stats(date)` | 7 | resting HR, Garmin 7-day avg resting HR, avg stress, body battery high/low |
| `get_training_readiness(date)` | 7 | readiness score, acute load, Garmin weekly avg HRV |

That is 22 calls. Don't call `get_activity` per activity, don't
fetch full sleep or stress time series, and don't hand the work to
a subagent. The summaries above are enough.

`get_training_readiness` returns several snapshots per day. Use the
earliest one (the wake-up reading).

**Do not fabricate a missing metric.** If Garmin has no HRV data for
a night, that night has no HRV. Don't estimate, interpolate, or
carry over a number from another day.

## How to build the report

1. Pull the 22 calls above.
2. Compute per-section aggregates and flag notable days (see
   `metrics.md` for exact definitions and thresholds).
3. Classify every claim as DATA, OBSERVATION, or INTERPRETATION.
   Read `interpretation-guidelines.md` before writing a single
   sentence of prose. This is the part people get wrong.
4. Write your prose (executive summary, things to watch, and 1 to 3
   DATA / OBSERVATION / INTERPRETATION examples) following
   `report-template.md`. Don't reorder sections, don't invent new
   ones.
5. **Always** build the web report and open it in Chrome (see below).
   This is the deliverable. Don't write your own HTML, don't paste the
   full report in the chat.
6. Reply in the chat with only the executive summary and the path of
   the page you opened.
7. Only if the user asks for a PDF: run `scripts/generate_charts.py`
   then `scripts/generate_pdf.py` (see below).

## Web report (always)

Write the 7 days to `output/week.json`, in the shape shown at the
top of `scripts/generate_charts.py` (one entry per day, `null` for
missing values), plus your prose:

```
"narrative": {
  "summary": ["3 to 5 sentences, 25 words max each"],
  "things_to_watch": ["hedged, non-medical, 25 words max each"],
  "interpretations": [
    {"data": "...", "observation": "...", "interpretation": "..."}
  ]
}
```

Then run these two commands exactly as written. They need nothing
but `python3`; don't check anything first.

```
$ python3 .claude/skills/garmin-weekly-performance-report/scripts/generate_html.py \
    --input output/week.json --output output/weekly-report.html
$ .claude/skills/garmin-weekly-performance-report/scripts/open_in_chrome.sh output/weekly-report.html
```

The script computes every number, chart and notable day from the
data. Your job is the prose. The page is dark mode, self-contained,
and works offline.

## PDF (only if a PDF is requested)

`scripts/generate_charts.py` writes PNGs for:

- training duration by day
- sleep duration by day
- resting HR vs Garmin's 7-day average
- HRV vs Garmin's weekly average
- acute load vs training readiness

`scripts/generate_pdf.py` lays those charts and the report content
into a single minimal, grayscale, printable PDF.

Run them from the repo root with the project virtualenv (paths
are relative to the repo root, not to this Skill's directory):

```
$ .venv/bin/python .claude/skills/garmin-weekly-performance-report/scripts/generate_charts.py \
    --input output/week.json --output-dir output/charts/
$ .venv/bin/python .claude/skills/garmin-weekly-performance-report/scripts/generate_pdf.py \
    --input output/week.json --charts-dir output/charts/ --output output/weekly-report.pdf
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

- `metrics.md` — what each metric means, which Garmin baseline it
  is compared against, what counts as "notable."
- `report-template.md` — the exact section structure to fill in.
- `interpretation-guidelines.md` — DATA / OBSERVATION /
  INTERPRETATION rules and banned phrases.
- `scripts/generate_html.py` — the dark-mode web report.
- `scripts/open_in_chrome.sh` — opens it in Chrome (or Chromium).
- `scripts/generate_charts.py` — chart images for the PDF.
- `scripts/generate_pdf.py` — PDF assembly.
- `scripts/weekly_metrics.py` — the numbers both reports share.

Read `metrics.md` and `report-template.md` before generating a
report for the first time in a session. You don't need to re-read
this file's neighbors on every single run once you know the job —
that's what progressive disclosure is for.
