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
    font-size: 0.8em;
  }
---

<!--
WORKSHOP-SLIDES.md -- a Marp-compatible version of WORKSHOP.md.

Render with:  marp WORKSHOP-SLIDES.md -o slides.pdf

WORKSHOP.md is the source of truth and what you present from. This
exists in case you need slides on a projector that isn't your
terminal.
-->

```
 █████╗ ██╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██║    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║    ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║    ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║██║    ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝
```

designing reliable AI workflows

---

## Agenda

```
00:00   What Is a Skill?             5 min
00:05   Without a Skill              5 min
00:10   Anatomy of a Skill           5 min
00:15   Build one by hand           10 min
00:25   Test it, fix it              5 min
00:30   MCP vs Skill                 5 min
00:35   Advanced Patterns           10 min
00:45   Why the extra files          5 min
00:50   Other patterns               5 min
00:55   Questions and Discussion
```

The same prompt is evaluated at three stages to demonstrate the effect
of added guidance.

---

## What Is a Skill?

```
MODEL        knows things
MCP / TOOLS  can do things
SKILLS       know how WE do things
```

Prompts solve a task. Skills encode how your team solves a class of
tasks.

---

## Without a Skill

```
Create a report about my last week.
```

```
Which metrics? Which days? How long?
Table? Essay? File?
What is it allowed to say about my health?
```

It must either request clarification or make assumptions, often beyond
the intended scope.

---

## Anatomy of a Skill

```
.claude/skills/
└── weekly-performance-report/
    └── SKILL.md
```

```
---
name: ...             <- what it is called
description: ...      <- WHEN to use it
---
...                   <- HOW to do the job
```

100 skills installed does not mean 100 skills in context.

---

## Build one by hand

```
1. Period: the last 7 days, ending yesterday.
2. Call get_stats and get_sleep_summary. Nothing else.
3. Reply with this table and nothing more:
   | Day | Resting HR | Sleep score |
4. Missing value: write "-". Never guess.
5. No medical advice.
```

Nineteen lines. No code.

---

## Test it, fix it

```
Create a report about my last week.
Create a report about my last 3 days.
```

```
WRITE IT DOWN -> TEST -> FIX -> REPEAT
```

---

## MCP vs Skill

```
MCP:     "What can the agent access?"
SKILL:   "How should the agent do this job?"
```

MCP gives the agent tools. Skills teach the agent how we use them.

---

## Level up

```
weekly-performance-report/
├── SKILL.md
├── metrics.md
├── report-template.md
├── interpretation-guidelines.md
└── scripts/   <- web report, charts, PDF
```

The same prompt, now with the complete Skill. The web report opens.

---

## Why the extra files

```
THE MODEL writes     the summary, what to watch
THE SCRIPT draws     every number, chart, flagged day
```

```
DATA            HRV 39 ms, weekly baseline 44 ms
OBSERVATION     11% below average that night
INTERPRETATION  coincided with the longest run
```

Skills are code. Code has performance bugs: 11 minutes -> 3.

---

## Other patterns

```
Developer: "Deploy this."
AI:        "I need clarification on 17 points."

Developer: "Deploy this."   (with a Skill)
AI:        "I know the drill."
```

incident-response · pull-request-review · release-readiness

---

# Encode recurring instructions once

and reuse them consistently.

```
$ exit
```
