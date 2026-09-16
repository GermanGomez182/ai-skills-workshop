# Demo 2: with the Skill

> PRESENTER PREP -- rehearsal material, not for the shared screen.
> `WORKSHOP.md` has the audience-facing version of this section.

Same Garmin MCP. Same agent. Only difference:
`.claude/skills/garmin-weekly-performance-report/` now exists.

## The prompt

Exactly the same one. Do not improve it.

```
Create a report about my last week.
```

## What should happen this time

- No clarifying questions about scope, period, or format --
  the Skill already answers those.
- The agent retrieves the previous 7 complete days, plus enough
  history for a previous-week and 4-week comparison.
- Output follows `report-template.md`'s section order exactly.
- Claims are separated into DATA / OBSERVATION / INTERPRETATION,
  per `interpretation-guidelines.md`.
- Missing metrics are reported as missing, not filled in.
- If you ask for a PDF, it's grayscale, dense, and boring in the
  way a real ops report is boring.

## Record what actually happened

```
WITH SKILL

Follow-up questions:      ?
Tool calls:                ?
Manual instructions:      ?
Missing requirements:      ?
Time to result:            ?
Format compliance:        ?
Consistency:                ?
```

If the agent still asks a clarifying question here, that's not a
failure of the demo -- it's a note for what the Skill should
encode next. Skills are code. Code has bugs.
