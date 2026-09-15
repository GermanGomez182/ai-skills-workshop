# Metrics reference

What each metric means for this report, and what counts as a
change worth mentioning. If a metric isn't listed here, don't
invent a definition for it — ask, or leave it out.

## Training

| Metric | Definition | Meaningful change |
|---|---|---|
| Total training duration | Sum of activity durations, in minutes, for the week | ±15% vs previous week |
| Activity count | Number of logged activities | any change of 2+ |
| Activity distribution | Breakdown by type (run/bike/strength/swim/other) | a type disappearing or appearing |
| Training load | Sum of per-activity training load for the week | ±20% vs previous week |

## Recovery

| Metric | Definition | Meaningful change |
|---|---|---|
| Resting HR | Average of daily resting HR readings | ±3 bpm vs previous week |
| HRV | Average of daily overnight HRV readings | ±10% vs previous week |
| Body Battery | Average daily max and average daily min | ±10 points on either |
| Training readiness | Average of daily readiness score | ±10 points vs previous week |

## Sleep

| Metric | Definition | Meaningful change |
|---|---|---|
| Sleep duration | Average nightly duration for the week | ±10% vs previous week |
| Sleep score | Average nightly score for the week | ±8 points vs previous week |
| Consistency | Std. deviation of nightly duration | flag if it roughly doubles vs previous week |

## Stress

| Metric | Definition | Meaningful change |
|---|---|---|
| Stress (avg) | Average daily stress score | ±15% vs previous week |

## Comparison windows

- **Previous week** — the 7 days immediately before the current
  period.
- **4-week baseline** — the 4 most recent complete weeks, current
  week included, averaged.

## Missing data

If a metric has no data point for a given day, exclude that day
from the average for that metric and say so in the report (e.g.
"HRV available for 5 of 7 days"). Never average in a zero or a
carried-over value.

## Rounding

- Durations: nearest minute, presented as `Xh YYm`.
- HR / HRV: nearest whole unit.
- Scores (sleep score, readiness, body battery): nearest whole
  number.
- Percent changes: nearest whole percent.
