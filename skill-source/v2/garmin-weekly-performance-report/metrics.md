# Metrics reference

What each metric means for this report, and what counts as a
notable day. If a metric isn't listed here, don't invent a
definition for it — ask, or leave it out.

The report covers **7 days only**. There is no previous week to
compare against. Instead, each day is compared against the
baseline **Garmin itself** calculated for that day. We don't
compute baselines; Garmin already did.

The thresholds below are **ours** (this Skill's), not Garmin's.
When you mention one, don't attribute it to Garmin.

## Training

| Metric | Source | Definition | Notable |
|---|---|---|---|
| Total training duration | `get_activities_by_date` | Sum of activity durations for the week | report only |
| Activity count | `get_activities_by_date` | Number of logged activities | report only |
| Activity distribution | `get_activities_by_date` | Count per activity type | report only |
| Rest days | `get_activities_by_date` | Days with no activity | report only |
| Acute load | `get_training_readiness` | Garmin's rolling acute load, first day vs last day | change of ±20% |

## Recovery

| Metric | Source | Compared against | Notable day |
|---|---|---|---|
| Resting HR | `get_stats` | Garmin's 7-day avg resting HR for that day | 3+ bpm above it |
| HRV | `get_sleep_summary` | Garmin's weekly avg HRV for that day (`get_training_readiness`) | 10%+ below it |
| Training readiness | `get_training_readiness` | Garmin's own scale | below 50 (Garmin "low" or worse) |
| Body Battery | `get_stats` | — | report only: avg daily high and low |

## Sleep

| Metric | Source | Compared against | Notable night |
|---|---|---|---|
| Sleep duration | `get_sleep_summary` | — | report only: average and shortest night |
| Sleep score | `get_sleep_summary` | Garmin's own scale | below 60 (Garmin "poor") |

## Stress

| Metric | Source | Compared against | Notable day |
|---|---|---|---|
| Stress (avg) | `get_stats` | Garmin's own scale | 51 or more (Garmin "medium" or higher) |

## Missing data

If a metric has no data point for a given day, exclude that day
from the average for that metric and say so in the report (e.g.
"HRV available for 6 of 7 days"). Never average in a zero or a
carried-over value.

## Rounding

- Durations: nearest minute, presented as `Xh YYm`.
- HR / HRV: nearest whole unit.
- Scores (sleep score, readiness, body battery, stress): nearest
  whole number.
- Percent changes: nearest whole percent.
