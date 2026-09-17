# Interpretation guidelines

This is the part of the Skill that keeps the report honest. Read
it before writing prose, not after.

## Three layers, never mixed

**DATA** — a number, directly from the source. No adjectives.

**OBSERVATION** — a comparison between numbers. Still no
explanation of *why*.

**INTERPRETATION** — a cautious, non-medical read of what the
observation might mean. Always hedged. Never a diagnosis.

### Example

```
DATA

Saturday overnight HRV:   39 ms
Garmin weekly avg HRV:    44 ms

OBSERVATION

HRV was 11% below Garmin's own
weekly average that night.

INTERPRETATION

This coincided with the longest
run of the week, the same day.
```

Notice what the interpretation does *not* say: it does not say the
run caused the HRV dip. It says the two things happened in the same
window. That distinction is the whole job.

## Hard rules

- **No medical diagnoses.** Not even softened ones.
- **No inferring injury.** A spike in resting HR is a data point,
  not a diagnosis of an injury in progress.
- **No causality from correlation.** Two metrics moving together in
  the same week is a coincidence worth naming, not a mechanism.
- **No fabricated metrics.** Missing data stays missing.

## Language

Use:

- "may indicate"
- "coincided with"
- "is consistent with"
- "could be worth monitoring"

Avoid entirely:

- "you are overtrained"
- "you are sick"
- "you have insomnia"
- "you are injured"

If a sentence needs one of the banned phrases to make its point,
the sentence is making a claim this Skill isn't allowed to make.
Rewrite it as an observation instead, or drop it.

## Quick self-check before shipping a report

- Does every INTERPRETATION sentence use hedged language?
- Could any sentence be read as medical advice? If yes, rewrite.
- Is there a claim with no DATA behind it? Delete it.
- Did two correlated metrics get described with a causal verb
  ("caused", "led to", "resulted in")? Replace with "coincided
  with" or similar.
- Does every weekday and date you name match a `date` in
  `output/week.json`, with the activities that day actually has?
  Work out weekday names from the date, never from memory. (A real
  run once put Sunday's runs on "Saturday, Sep 13".)
