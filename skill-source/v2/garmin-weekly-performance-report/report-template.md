# Report template

Fill this shape. Don't add sections, don't remove sections, don't
reorder them. If a section has nothing meaningful to say, write
"Nothing notable this week" instead of deleting the section.

```
WEEKLY PERFORMANCE REPORT

Period:
YYYY-MM-DD -> YYYY-MM-DD


EXECUTIVE SUMMARY

3 to 5 concise observations. Each one should be something a
reader can act on or at least remember. No filler sentences.


TRAINING

Total training time
Number of activities
Activity distribution
Rest days
Acute load, first day -> last day


RECOVERY

Resting HR (avg)
HRV (avg)
Body Battery (avg daily high / low)
Training readiness (avg)
Stress (avg)


SLEEP

Average duration
Shortest night
Average sleep score


NOTABLE DAYS

Only days that cross the thresholds in metrics.md, one line per
day and metric, with the Garmin baseline it was compared against.
If nothing crossed a threshold, say so plainly.


GARMIN BASELINES

What Garmin's own rolling numbers say at the end of the week:
7-day avg resting HR, weekly avg HRV, acute load.


THINGS TO WATCH

Non-medical observations that may be useful to monitor next
week. Framed as things to watch, not conclusions.
```

## Writing rules for this template

- The web report (`scripts/generate_html.py`) renders these sections
  in this order. The numbers come from the data; the executive
  summary and things to watch come from your `narrative`.
- Executive summary is written **last**, after every other
  section is done. It's a compression of the report, not a
  preview.
- Every number in the report must trace back to retrieved data.
  If you can't point to where a number came from, don't print it.
- Follow `interpretation-guidelines.md` for how DATA, OBSERVATION,
  and INTERPRETATION are worded and separated.
