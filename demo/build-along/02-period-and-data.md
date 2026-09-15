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
