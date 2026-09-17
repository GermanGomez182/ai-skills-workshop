---
name: garmin-weekly-performance-report
description: Garmin health report with resting heart rate and sleep score per day. Use when the user asks for a report about their last week, their recent days, their sleep or their heart rate.
---

# Garmin report

1. Period: the last 7 days, ending yesterday. If the user asks for
   a number of days ("my last 3 days"), use that instead.
2. For each day, call `get_stats` (resting HR) and
   `get_sleep_summary` (sleep score). All calls in parallel.
   Nothing else.
3. Reply with this table and nothing more:

   | Day | Resting HR | Sleep score |

   Last row: the average of each column.
4. Missing value: write "-". Never guess a number.
5. No medical advice. No recommendations.
