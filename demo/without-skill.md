# Demo 1: without a Skill

> PRESENTER PREP -- rehearsal material. Do not open this file on
> the shared screen during the talk; `WORKSHOP.md` already has the
> audience-facing version of this section. Use this beforehand to
> rehearse, or right after the talk to write down what actually
> happened.

Garmin MCP is connected. No Skill installed. The agent can reach
every metric, it just has no idea what you actually want.

## The prompt

```
Create a report about my last week.
```

## What tends to go wrong

Watch for some subset of these, live:

- What does "report" mean?
- Which metrics matter?
- Should training and sleep be combined?
- Should it compare against previous weeks?
- What period exactly means "last week"?
- Should it generate charts?
- Should the output be Markdown or PDF?
- What constitutes an important change?
- What should the report emphasize?
- Should it make recommendations?
- What should it not infer?

The agent has access to everything and a plan for nothing.

## Record what actually happened

Fill this in during rehearsal, or immediately after the section
ends (on your notes monitor, not the shared one). Don't pre-fill
it before you've actually run the demo -- if you already know the
answer, it's not a demo, it's a slide.

```
WITHOUT SKILL

Follow-up questions:      ?
Tool calls:                ?
Manual instructions:      ?
Missing requirements:      ?
Time to result:            ?
Format compliance:        ?
Consistency:                ?
```

`Consistency` means: if you ran this same prompt three times in a
row, would you get three different report shapes? You probably
would. That's worth saying out loud, not just writing down.
