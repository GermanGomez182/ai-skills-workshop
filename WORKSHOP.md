```
$ cat /etc/motd

 █████╗ ██╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██║    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║    ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║    ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║██║    ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

              designing reliable AI workflows


$ _















```


[00] AGENDA
===========

```
00:00   WTF is a Skill?              5 min
00:05   No Skill                     5 min
00:10   Anatomy of a Skill           5 min
00:15   Build one by hand           10 min
00:25   Test it, fix it              5 min
00:30   MCP vs Skill                 5 min
00:35   Level up                    10 min
00:45   Why the extra files          5 min
00:50   Other patterns               5 min
00:55   Q&A
```

Same prompt, three times. Watch what changes.






















[01] WTF IS A SKILL?
=====================

```
MODEL
knows things

MCP / TOOLS
can do things

SKILLS
know how WE do things
```

```
  Model
    +
  Tools / MCP
    +
  Skills
    =
  Specialized Agent
```

```
Prompts solve a task.

Skills encode how your team solves
a class of tasks.
```
























[02] NO SKILL
===============

An agent connected to a fitness-data service through an MCP server.
It can read activities, sleep, heart rate, stress, and training
readiness from a supplied dataset.

The prompt. Deliberately vague, like every real request:

```
Create a report about my last week.
```

The agent has to guess everything:

```
Which metrics?
Which days?
How long?
Table? Essay? File?
What is it allowed to say about my health?
```

So it asks, or it guesses. Usually it guesses big.

What I actually wanted:

```
Resting heart rate and sleep score.
One line per day.
That's it.
```












[03] ANATOMY OF A SKILL
=========================

A Skill is a folder containing a markdown file.

```
.claude/skills/
└── weekly-performance-report/
    └── SKILL.md
```

It has to live in `.claude/skills/`. Anywhere else, it's just a
folder with markdown in it. (We learned that one live.)

`SKILL.md` has two parts:

```
---
name: ...             <- what it is called
description: ...      <- WHEN to use it
---

...                   <- HOW to do the job
```

The agent does not read every Skill all the time. It only sees
each `name` and `description`, and loads the rest when a request
matches.

```
100 SKILLS INSTALLED

does not mean

100 SKILLS IN CONTEXT
```

So the description is the most important line in the file.


[04] BUILD ONE BY HAND
========================

Inside `demo/`, the empty project. A Skill only counts if it lives
in `.claude/skills/<name>/`, next to the project it serves:

```
$ cd demo
$ mkdir -p .claude/skills/weekly-performance-report
$ nvim .claude/skills/weekly-performance-report/SKILL.md
```

```
---
name: weekly-performance-report
description: Weekly performance report with resting heart rate and sleep score per day. Use when the user asks for a report about a recent period, sleep, or heart rate.
---

# Weekly performance report

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
```

Nineteen lines. No code. Every line is a decision the agent would
otherwise have to guess:

```
which days              -> 1
which data, which calls -> 2
what shape              -> 3
what if it's missing    -> 4
what it must never do   -> 5
```

Restart Claude so it finds the new Skill:

```
$ ../scripts/claude.sh
```


[05] TEST IT, FIX IT
======================

Same prompt as [02]. Character for character:

```
Create a report about my last week.
```

Look at the difference:

```
- no questions
- a few small tool calls instead of a tour of the API
- the table I asked for, nothing else
- same shape every time I run it
```

Now use the parameter, in plain English:

```
Create a report about my last 3 days.
```

Look at the Day column:

```
| Day        | Resting HR | Sleep score |
| 2026-09-14 | 56         | 58          |
```

I never said what a day looks like, so it chose. What you don't
write down, the model decides.

One line into step 3, restart, run it again:

```
Day column: weekday and day number, like "Mon 14".
```

```
WRITE IT DOWN -> TEST -> FIX -> REPEAT
```

A Skill is code. You read the output, change a line, run it again.


[06] MCP VS SKILL
===================

```
$ diff mcp skill
```

Look at what just happened:

```
MCP / DATA SERVICE              SKILL
==========                      =====

get_stats                       which days
get_sleep_summary               which calls
...and many more tools          which numbers
                                what shape

It knows HOW TO GET the data.   It knows WHAT WE WANT from it.
```

Not competitors. Different questions:

```
MCP:     "What can the agent access?"

SKILL:   "How should the agent do this job?"
```

```
MCP gives the agent tools.

Skills teach the agent
how we use those tools.
```


[07] LEVEL UP
===============

Same Skill. Version 2. Built for a real weekly report.

```
$ ../scripts/install-skill.sh v2
$ ../scripts/claude.sh
```

```
.claude/skills/weekly-performance-report/
├── SKILL.md                      <- same idea as yours, longer
├── metrics.md                    <- what counts as "notable"
├── report-template.md            <- the sections, in order
├── interpretation-guidelines.md  <- how to talk about health data
└── scripts/
    ├── generate_html.py          <- builds the web report
    ├── open_in_chrome.sh         <- opens it
    └── ...                       <- charts, PDF, shared numbers
```

Same prompt. Third time:

```
Create a report about my last week.
```

```
$ _
```


[08] WHY THE EXTRA FILES
==========================

Same shape as the v1 you just watched me type. It just grew.

**References, not one giant file.** `SKILL.md` stays short and
points at the other files. The agent reads them when it needs them.

**The model writes words. Scripts draw numbers.**

```
THE MODEL writes     the summary, what to watch
THE SCRIPT draws     every number, chart, flagged day
```

The model can't fudge a chart, and the page looks the same every
week.

It also makes mistakes visible. In rehearsal the model wrote that
my runs were on "Saturday". The chart, drawn from the data, put
them on Sunday. The chart was right. The fix was one new check in
`interpretation-guidelines.md`.

**Health data needs manners.** Say what happened, not why:

```
DATA            HRV 39 ms, weekly baseline 44 ms
OBSERVATION     11% below average that night
INTERPRETATION  coincided with the longest run of the week
```

"Coincided with". Never "caused by".

**Skills are code. Code kas performance bugs.** The first version
of this Skill asked for four weeks of history: about eleven minutes
per run. One paragraph changed it to one week: about three.

Design rules, short version:

```
1. One clear job.
2. A description that says WHEN.
3. Decisions, not obvious facts.
4. Short SKILL.md, references for the rest.
5. Examples and boundaries.
6. Scripts for anything that must be exact.
7. Test it. Fix it. Version it.
```


[09] OTHER PATTERNS
=====================

Speed round.

```
WITHOUT SKILL

Developer: "Deploy this."
AI:        "Great. I have 17 questions."


WITH aws-production-deployment/

Developer: "Deploy this."
AI:        "I know the drill."
```

```
$ ls .claude/skills/

incident-response/     who gets paged, what "resolved" means
pull-request-review/   what blocks a merge HERE
release-readiness/     the checklist in one senior's head
meeting-notes/         decisions, owners, due dates
```

```
Today:      the senior engineer knows how production works.

Tomorrow:   production-deployment/SKILL.md
```

```
Enterprise AI Architecture, current version

Step 1:  Ask the senior engineer.
Step 2:  Hope they still work here.
```


[10] THE POINT
================

```
THE POINT
=========

Prompts solve a task.

Skills encode how your team
solves a class of tasks.


MCP gives the agent access.

Skills give the agent procedure.


Don't teach the AI
the same thing twice.
```

```
$ exit
```
