---
marp: true
theme: default
paginate: true
backgroundColor: white
style: |
  section {
    font-family: monospace;
  }
  pre {
    font-size: 0.85em;
  }
---

<!--
WORKSHOP-SLIDES.md -- a Marp-compatible export of WORKSHOP.md.

Render with:  marp WORKSHOP-SLIDES.md -o slides.pdf
(or the Marp CLI / VS Code extension of your choice)

This is a secondary artifact. WORKSHOP.md is the source of truth
and the thing you actually present from. This exists in case you
ever need slides on a projector that isn't your terminal.
-->

```
 █████╗ ██╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██║    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║    ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║    ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║██║    ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝
```

teaching agents how we work

**Germán Nicolás Gómez**
AI Solutions Architect Lead

---

## Agenda

```
00:00   WTF is a Skill?             5 min
00:05   Garmin without Skill        8 min
00:13   MCP vs Skill                7 min
00:20   Garmin with Skill           8 min
00:28   Inspect the Skill           5 min
00:33   Build a Skill together     15 min
00:48   Run the Skill               5 min
00:53   Other patterns              5 min
00:58   Q&A
```

---

## WTF is a Skill?

```
MODEL        knows things
MCP / TOOLS  can do things
SKILLS       know how WE do things
```

---

## The equation

```
  Model
    +
  Tools / MCP
    +
  Skills
    =
  Specialized Agent
```

---

## The takeaway

Prompts solve a task.

Skills encode how your team solves
a class of tasks.

---

## Without a Skill

Garmin MCP connected. No Skill.

```
Create a report about my last week.
```

AI: *"Sure! Before I begin, I have seventeen questions."*

---

## What goes wrong

```
What does "report" mean?
Which metrics matter?
What period is "last week"?
Charts? PDF or Markdown?
What's a meaningful change?
Should it make recommendations?
```

---

## Watch for

```
- follow-up questions asked
- tool calls made
- manual instructions supplied
- missing requirements exposed
- time to result
- format compliance
- consistency across runs
```

---

## MCP vs Skill

```
TOOLS answer:
"What can the agent access or execute?"

SKILLS answer:
"How should the agent perform this job?"
```

Not competitors. Different questions.

---

## Garmin MCP

```
Gives the agent ACCESS to:

- sleep, activities, HR, HRV
- training load, recovery metrics

It knows HOW TO GET the data.
```

---

## Weekly Fitness Report Skill

```
Teaches the agent:

- which data matters
- what period, how to compare
- what sections, what charts
- what not to infer

It knows HOW TO DO THE JOB.
```

---

## The line

```
MCP gives the agent tools.

Skills teach the agent
how we use those tools.
```

---

## With a Skill

```
$ ls .claude/skills/garmin-weekly-performance-report/

SKILL.md
metrics.md
report-template.md
interpretation-guidelines.md
scripts/
```

---

## DATA / OBSERVATION / INTERPRETATION

```
DATA
Average sleep: 6h 18m

OBSERVATION
Sleep decreased 11% vs previous week.

INTERPRETATION
This coincided with an increase
in training load.
```

Correlation, not causality. Always hedged.

---

## Report shape

```
WEEKLY PERFORMANCE REPORT

EXECUTIVE SUMMARY
TRAINING
RECOVERY
SLEEP
NOTABLE CHANGES
4-WEEK CONTEXT
THINGS TO WATCH
```

---

## Same prompt, again

```
Create a report about my last week.
```

Same string as before. No edits.

---

## The comparison

Same seven things from before. Talk through the delta out loud --
what changed isn't the model, it's that the team's judgment calls
got written down once.

---

## Inspect the Skill

```
:e .claude/skills/garmin-weekly-performance-report/SKILL.md
```

This is the moment a slide deck can't do.

---

## Build one: the progression

```
DEFINE THE JOB
DEFINE THE RULES
DEFINE REQUIRED CONTEXT
ADD EXAMPLES
DEFINE WHAT NOT TO DO
TEST
ITERATE
```

---

## Progressive disclosure

```
100 SKILLS INSTALLED

does not mean

100 SKILLS IN CONTEXT
```

```
discover -> select -> load -> execute
```

---

## Skill design principles

```
1. One clear job.
2. Strong description.
3. Encode decisions, not obvious facts.
4. Prefer references over giant files.
5. Include examples.
6. Include boundaries.
7. Make outputs testable.
8. Treat Skills as code.
```

---

## Organizational Skills

```
Today:      senior engineer knows how
            production works.

Tomorrow:   production-deployment/SKILL.md
```

```
Tribal knowledge -> version controlled knowledge
```

---

## Run it

```
$ ./scripts/run-demo.sh
$ ./scripts/generate-sample-report.sh
```

---

## Other patterns: AWS

```
WITHOUT SKILL
Developer: "Deploy this."
AI: "Great. I have 17 questions."

WITH SKILL
Developer: "Deploy this."
AI: "I know the drill."
```

---

## Other patterns: a few more

```
incident-response
pull-request-review
release-readiness
```

Your team's actual process, version controlled.

---

## Non-developer example

```
With engineering-meeting/:

Decisions
Action Items    Owner   Due Date
Open Questions
Technical Risks
Follow-ups
```

---

# THE POINT

Prompts solve a task.

Skills encode how your team
solves a class of tasks.

---

# THE POINT (cont.)

MCP gives the agent access.

Skills give the agent procedure.

---

# Don't teach the AI

the same thing twice.

```
$ _
```
