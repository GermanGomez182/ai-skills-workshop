### Workshop
# AI Skills: teaching agents how we work

Germán Nicolás Gómez · AI Solutions Architect Lead

---

### Agenda
## Same prompt, three times. Watch what changes.

| Time | Topic | Length |
|---|---|---|
| 00:00 | WTF is a Skill? | 5 min |
| 00:05 | No Skill | 5 min |
| 00:10 | Anatomy of a Skill | 5 min |
| 00:15 | Build one by hand | 10 min |
| 00:25 | Test it, fix it | 5 min |

---

### Agenda
## Then we level it up

| Time | Topic | Length |
|---|---|---|
| 00:30 | MCP vs Skill | 5 min |
| 00:35 | Level up | 10 min |
| 00:45 | Why the extra files | 5 min |
| 00:50 | Other patterns | 5 min |
| 00:55 | Q&A | |

---

# WTF is a Skill?

Model + Tools + Skills = a specialized agent.

---

### [01] The stack
## Each layer answers a different question

- **Model**: knows things
- **MCP / Tools**: can do things
- **Skills**: know how WE do things

---

> Prompts solve a task. Skills encode how your team solves a class of tasks.

---

# No Skill

Claude Code, connected to my real Garmin account through an MCP server.

---

### [02] No Skill
## A vague prompt, like every real request

```
Create a report about my last week.
```

The agent can read my activities, sleep, heart rate, stress and training readiness. Real data.

---

### [02] No Skill
## The agent has to guess everything

- Which metrics?
- Which days?
- How long?
- Table? Essay? File?
- What is it allowed to say about my health?

So it asks, or it guesses. Usually it guesses big.

---

### [02] No Skill
## What I actually wanted

- Resting heart rate and sleep score
- One line per day
- That's it

---

# Anatomy of a Skill

A Skill is a folder with a markdown file in it.

---

### [03] Anatomy
## It has to live in .claude/skills/

```
.claude/skills/
└── garmin-weekly-performance-report/
    └── SKILL.md
```

Anywhere else, it's just a folder with markdown in it. (We learned that one live.)

---

### [03] Anatomy
## SKILL.md has two parts: when, and how

```
---
name: ...             <- what it's called
description: ...      <- WHEN to use it
---

...                   <- HOW to do the job
```

---

### [03] Anatomy
## 100 Skills installed does not mean 100 Skills in context

The agent only sees each `name` and `description`, and loads the rest when a request matches.

> So the description is the most important line in the file.

---

# Build one by hand

Inside `demo/`, the empty project.

---

### [04] Build it
## Create the folder next to the project it serves

```bash
$ cd demo
$ mkdir -p .claude/skills/garmin-weekly-performance-report
$ nvim .claude/skills/garmin-weekly-performance-report/SKILL.md
```

---

### [04] Build it
## The frontmatter says when

```
---
name: garmin-weekly-performance-report
description: Garmin health report with resting heart
  rate and sleep score per day. Use when the user asks
  for a report about their last week, their recent
  days, their sleep or their heart rate.
---
```

---

### [04] Build it
## The body says how

```
# Garmin report

1. Period: the last 7 days, ending yesterday. If the user
   asks for a number of days ("my last 3 days"), use that.
2. For each day, call `get_stats` (resting HR) and
   `get_sleep_summary` (sleep score). All calls in
   parallel. Nothing else.
3. Reply with this table and nothing more:
   | Day | Resting HR | Sleep score |
   Last row: the average of each column.
4. Missing value: write "-". Never guess a number.
5. No medical advice. No recommendations.
```

---

### [04] Build it
## Nineteen lines. No code. Every line is a decision.

| The agent would guess | Step |
|---|---|
| Which days | 1 |
| Which data, which calls | 2 |
| What shape | 3 |
| What if it's missing | 4 |
| What it must never do | 5 |

Restart Claude so it finds the new Skill: `../scripts/claude.sh`

---

# Test it, fix it

Same prompt as before. Character for character.

---

### [05] Test it
## Same prompt, a different result

```
Create a report about my last week.
```

- No questions
- A few small tool calls instead of a tour of the API
- The table I asked for, nothing else
- Same shape every time I run it

---

### [05] Test it
## Use the parameter, in plain English

```
Create a report about my last 3 days.
```

Look at the Day column:

| Day | Resting HR | Sleep score |
|---|---|---|
| 2026-09-14 | 56 | 58 |

---

### [05] Fix it
## What you don't write down, the model decides

I never said what a day looks like, so it chose. One line into step 3, restart, run it again:

```
Day column: weekday and day number, like "Mon 14".
```

---

### [05] Fix it
## A Skill is code. Read the output, change a line, run it again.

1. Write it down
2. Test
3. Fix
4. Repeat

---

# MCP vs Skill

Not competitors. Different questions.

---

### [06] MCP vs Skill
## One knows how to get the data. The other knows what we want.

| Garmin MCP | Skill |
|---|---|
| `get_stats` | which days |
| `get_sleep_summary` | which calls |
| ...and many more tools | which numbers, what shape |
| Knows HOW TO GET the data | Knows WHAT WE WANT from it |

---

### [06] MCP vs Skill
## Different questions

- **MCP**: What can the agent access?
- **Skill**: How should the agent do this job?

> MCP gives the agent tools. Skills teach the agent how we use those tools.

---

# Level up

Same Skill. Version 2. Built for a real weekly report.

---

### [07] Level up
## Version 2 grows references and scripts

```
garmin-weekly-performance-report/
├── SKILL.md                      <- same idea, longer
├── metrics.md                    <- what counts as "notable"
├── report-template.md            <- the sections, in order
├── interpretation-guidelines.md  <- how to talk about health
└── scripts/
    ├── generate_html.py          <- builds the web report
    ├── open_in_chrome.sh         <- opens it
    └── ...                       <- charts, PDF, shared numbers
```

---

### [07] Level up
## Same prompt. Third time.

```bash
$ ../scripts/install-skill.sh v2
$ ../scripts/claude.sh
```

```
Create a report about my last week.
```

---

# Why the extra files

Same shape as the v1 you just watched me type. It just grew.

---

### [08] References
## References, not one giant file

`SKILL.md` stays short and points at the other files. The agent reads them when it needs them.

---

### [08] Scripts
## The model writes words. Scripts draw numbers.

- **The model writes**: the summary, what to watch
- **The script draws**: every number, chart, flagged day

The model can't fudge a chart, and the page looks the same every week.

---

### [08] Scripts
## Scripts make mistakes visible

In rehearsal the model wrote that my runs were on "Saturday". The chart, drawn from the data, put them on Sunday.

The chart was right. The fix was one new check in `interpretation-guidelines.md`.

---

### [08] Manners
## Health data needs manners: say what happened, not why

| Layer | Example |
|---|---|
| Data | HRV 39 ms, Garmin average 44 ms |
| Observation | 11% below average that night |
| Interpretation | *coincided with* the longest run of the week |

"Coincided with". Never "caused by".

---

### [08] Performance
## Skills are code. Code has performance bugs.

- **Before**: four weeks of history, about 11 minutes per run
- **After**: one week of history, about 3 minutes
- **The fix**: one paragraph

---

### [08] Design rules
## Design rules, short version

1. One clear job.
2. A description that says WHEN.
3. Decisions, not obvious facts.
4. Short `SKILL.md`, references for the rest.
5. Examples and boundaries.
6. Scripts for anything that must be exact.
7. Test it. Fix it. Version it.

---

# Other patterns

Speed round.

---

### [09] Other patterns
## Without a Skill vs with one

| | Developer | AI |
|---|---|---|
| Without Skill | "Deploy this." | "Great. I have 17 questions." |
| With `aws-production-deployment/` | "Deploy this." | "I know the drill." |

---

### [09] Other patterns
## Skills your team could write tomorrow

- `incident-response/`: who gets paged, what "resolved" means
- `pull-request-review/`: what blocks a merge HERE
- `release-readiness/`: the checklist in one senior's head
- `meeting-notes/`: decisions, owners, due dates

---

### [09] Other patterns
## Today, the senior engineer knows how production works

Tomorrow: `production-deployment/SKILL.md`

> Enterprise AI Architecture, current version. Step 1: ask the senior engineer. Step 2: hope they still work here.

---

### [10] The point
## Access is not procedure

- **Prompts** solve a task
- **Skills** encode how your team solves a class of tasks
- **MCP** gives the agent access
- **Skills** give the agent procedure

---

> Don't teach the AI the same thing twice.

---

# Q&A

`$ exit`
