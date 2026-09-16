```
$ cat /etc/motd

 █████╗ ██╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██║    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║    ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║    ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║██║    ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

              teaching agents how we work


  Germán Nicolás Gómez
  AI Solutions Architect Lead


$ _
```


[00] AGENDA
===========

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

One continuous story. Not nine slides.


[01] WTF IS A SKILL?
=====================

Three things. Say them slowly.

```
MODEL
knows things

MCP / TOOLS
can do things

SKILLS
know how WE do things
```

Put together:

```
  Model
    +
  Tools / MCP
    +
  Skills
    =
  Specialized Agent
```

The takeaway, in one line:

```
Prompts solve a task.

Skills encode how your team solves
a class of tasks.
```

And the one you'll hear again at the end:

```
Don't teach the AI
the same thing twice.
```

We're going to demonstrate this, not describe it.


[02] WITHOUT SKILL
====================

The scenario: Garmin MCP is connected to Garmin Connect. The
agent can pull activities, sleep, HR, HRV, training load,
recovery, training readiness, stress, body battery. Real access,
real data.

No Skill installed yet.

```
$ ./scripts/demo-hide-skill.sh
```

New Claude Code session -- Skills load at session start, not mid-
conversation. Nothing about *this chat* changes between runs; only
what's on disk does.

```
$ ls .claude/skills/

ls: cannot access '.claude/skills/': No such file or directory
```

One prompt. Deliberately vague, because that's how real requests
show up in Slack:

```
Create a report about my last week.
```

Run it live. Let the questions happen.

Likely trouble, in no particular order:

```
What does "report" mean?
Which metrics matter?
Should training and sleep be combined?
Should it compare against previous weeks?
What period exactly means "last week"?
Should it generate charts?
Should the output be Markdown or PDF?
What constitutes an important change?
What should the report emphasize?
Should it make recommendations?
What should it not infer?
```

AI:

```
Sure! Before I begin,
I have seventeen questions.
```

While it runs, watch for:

```
- follow-up questions asked
- tool calls made
- manual instructions you had to supply
- missing requirements exposed
- time to result
- format compliance
- consistency (would two runs even look alike?)
```

Keep that list in mind. We're running the exact same prompt again
in a few minutes.


[03] MCP VS SKILL
===================

These are not competitors. They answer different questions.

```
TOOLS answer:

"What can the agent access or execute?"


SKILLS answer:

"How should the agent perform this job?"
```

Concretely, for this exact demo:

```
GARMIN MCP
==========

Gives the agent ACCESS to:

- sleep data
- activities
- heart rate
- HRV
- training load
- recovery metrics

It knows HOW TO GET the data.
```

```
WEEKLY FITNESS REPORT SKILL
===========================

Teaches the agent:

- which data matters
- what period to analyze
- how to compare weeks
- what sections to create
- what charts to generate
- what not to infer
- how the final report should look

It knows HOW TO DO THE JOB.
```

```
MCP gives the agent tools.

Skills teach the agent
how we use those tools.
```


[04] WITH SKILL
=================

Same MCP. Same agent. One new directory, in the one place Claude
Code actually looks for project Skills -- and a new session again,
same reason as [02]:

```
$ ./scripts/demo-restore-skill.sh
```

```
$ ls .claude/skills/

garmin-weekly-performance-report/
```

```
$ ls .claude/skills/garmin-weekly-performance-report/

SKILL.md
metrics.md
report-template.md
interpretation-guidelines.md
scripts/
```

A Skill anywhere else -- a top-level `skills/`, a `docs/` folder,
wherever felt tidy -- is just a directory Claude might stumble
into while exploring. It only becomes an installed Skill from
`.claude/skills/`. Ask us how we found that out.

What it teaches the agent, briefly:

- retrieve the previous 7 complete days
- compare current week / previous week / 4-week baseline
- pull training, recovery, sleep, stress, body battery,
  readiness -- whatever's available, nothing fabricated
- separate DATA, OBSERVATION, and INTERPRETATION
- never diagnose, never claim causality, hedge language
- fill one fixed report structure, every time
- optionally render a plain, grayscale PDF

The DATA / OBSERVATION / INTERPRETATION split, since it's the part
people get wrong in production:

```
DATA

Average sleep:
6h 18m

OBSERVATION

Sleep decreased 11%
compared with the previous week.

INTERPRETATION

This coincided with an increase
in training load.
```

Notice the interpretation doesn't say training *caused* the sleep
loss. Full rules: `interpretation-guidelines.md`.

Report shape (full version in `report-template.md`):

```
WEEKLY PERFORMANCE REPORT

Period: YYYY-MM-DD -> YYYY-MM-DD

EXECUTIVE SUMMARY
TRAINING
RECOVERY
SLEEP
NOTABLE CHANGES
4-WEEK CONTEXT
THINGS TO WATCH
```

Now, the exact same prompt as [02]. Character for character:

```
Create a report about my last week.
```

Same seven things to watch as before. Talk through the delta out
loud:

```
- follow-up questions asked
- tool calls made
- manual instructions you had to supply
- missing requirements exposed
- time to result
- format compliance
- consistency
```

What changed isn't the model. It's that the team's judgment calls
-- which period, which metrics, what counts as notable, what
language is safe -- got written down once, in a place the agent
reads before doing the job.


[05] INSPECT THE SKILL
========================

This is the moment PowerPoint can't do.

```
:e .claude/skills/garmin-weekly-performance-report/SKILL.md
```

```
$ cat .claude/skills/garmin-weekly-performance-report/SKILL.md
```

What to point at while you're in there:

- the `description:` field -- this is what makes the Skill
  *discoverable* without loading the whole thing (more in [06])
- the boundaries section -- what it refuses to do, and why that's
  written down instead of assumed
- the references out to `metrics.md` and
  `interpretation-guidelines.md` instead of one giant file


[06] BUILD ONE
================

A Skill is not magic. It's a directory, some files, and the
discipline to keep them boring. Watch it get built from nothing.

```
$ ./scripts/demo-hide-skill.sh

[ok] hidden: .claude/skills/garmin-weekly-performance-report -> .demo-backup/...
$ ls .claude/skills/
```

New session again -- old habit by now.

```
$ mkdir -p .claude/skills/garmin-weekly-performance-report
$ touch .claude/skills/garmin-weekly-performance-report/SKILL.md
```

We're pasting prepared fragments into each file, not freehand
composing paragraphs live -- nobody's here to watch prose get
written in real time, and a YAML frontmatter typo isn't a good use
of anyone's fifteen minutes.

One file at a time, say *why* each one exists before adding it:

```
.claude/skills/
└── garmin-weekly-performance-report/
    └── SKILL.md
```

- **SKILL.md** gets its job, its trigger phrases, and its rules
  (period, comparison windows, what data to pull) first.
- **metrics.md** -- because "meaningful change" needs a real
  threshold, not vibes.
- **report-template.md** -- because the shape of the report
  shouldn't get reinvented weekly.
- **interpretation-guidelines.md** -- because this is a health
  report and language matters. This is also where SKILL.md gets
  wired up to actually use these three files and the scripts.
- **boundaries**, back in SKILL.md -- what it must never do.
- **scripts/** -- charts and PDFs are a job for code, not prose.
  Copied in wholesale, not typed; nobody hand-writes matplotlib
  calls on stage either.

Restart once more -- the files exist now, this session just hasn't
looked yet -- then run the prompt from [02]/[04] again. Whatever's
missing or wrong is the next edit -- that's the iterate step, not
a failure.

The progression:

```
DEFINE THE JOB
      |
DEFINE THE RULES
      |
DEFINE REQUIRED CONTEXT
      |
ADD EXAMPLES
      |
DEFINE WHAT NOT TO DO
      |
TEST
      |
ITERATE
```

## Progressive disclosure

```
100 SKILLS INSTALLED

does not mean

100 SKILLS IN CONTEXT
```

```
discover
   |
select
   |
load
   |
execute
```

A good Skill has enough in its `description:` to be found and
picked correctly -- without forcing its full contents into context
on every single turn. That's the entire reason SKILL.md stays
short and points to `metrics.md` / `report-template.md` /
`interpretation-guidelines.md` instead of inlining them.

## Skill design principles

```
1. One clear job.
2. Strong description.
3. Encode decisions, not obvious facts.
4. Prefer references over giant SKILL.md files.
5. Include examples.
6. Include boundaries.
7. Make outputs testable.
8. Treat Skills as code.
```

- **One clear job.** This Skill writes a weekly report. It does
  not also triage your inbox.

- **Strong description.** It's the only part loaded before the
  Skill is selected. Vague descriptions mean the Skill never gets
  picked, or gets picked for the wrong job.

- **Encode decisions, not obvious facts.** Nobody needs a Skill to
  know sleep happens at night. They need one to know *your team's*
  threshold for "sleep dropped enough to mention."

- **Prefer references.** metrics.md exists so SKILL.md doesn't.

- **Include examples.** The DATA/OBSERVATION/INTERPRETATION block
  in [04] is worth more than a paragraph describing the rule.

- **Include boundaries.** What it must not do is as load-bearing
  as what it must do.

- **Make outputs testable.** A fixed report structure means you
  can actually check if the Skill did its job.

- **Treat Skills as code.** Version it, review it, iterate it.
  It breaks like code, so fix it like code.

## Organizational Skills

```
Today:

Senior engineer
knows how production works.
```

```
Tomorrow:

production-deployment/
    SKILL.md
```

```
Tribal knowledge
      |
Version controlled knowledge
```

Skills can capture:

- engineering standards
- deployment practices
- architecture patterns
- security rules
- incident procedures
- documentation standards
- reporting standards
- domain-specific workflows

```
Enterprise AI Architecture

Step 1:
Ask the senior engineer.

Step 2:
Hope they still work here.
```


[07] RUN IT
=============

```
$ ./scripts/run-demo.sh
```

The Skill already produced a report in [04] -- as text, because
nobody asked for a file. That's correct behavior, not a gap. Now
ask for the deliverable directly:

```
Now give me that as a PDF, with charts.
```

Ideally against live Garmin MCP data. Offline fallback:

```
$ ./scripts/generate-sample-report.sh

generating charts...
assembling pdf...
done: output/weekly-report.pdf
```

Open the result. Point at:

- the report structure matching `report-template.md` exactly
- a missing metric reported as missing, not guessed
- grayscale, dense, no wellness-app gradients


[08] OTHER PATTERNS
======================

Fast montage.

## AWS example

```
Developer:
"Deploy this FastAPI service to AWS."
```

Without a Skill:

```
Which compute service?
Lambda? ECS? EKS?
Terraform? CDK?
Networking? Secrets?
Observability? CI/CD?
Naming convention?
Environment strategy?
```

With `aws-production-deployment/`:

```
WITHOUT SKILL

Developer: "Deploy this."
AI: "Great. I have 17 questions."
```

```
WITH SKILL

Developer: "Deploy this."
AI: "I know the drill."
```

The Skill might encode: ECS Fargate, Terraform, ALB, Secrets
Manager, CloudWatch, GitHub Actions, dev/staging/prod, tagging
conventions, security and networking standards.

## A few more, picked short on purpose

```
$ ls .claude/skills/

garmin-weekly-performance-report/
aws-production-deployment/
incident-response/
```

- **incident-response** -- encodes your team's actual postmortem
  process: who gets paged, what gets timestamped, what "resolved"
  means before someone types it in Slack.
- **pull-request-review** -- your team's actual review bar, not a
  generic linter opinion. What blocks a merge here specifically.
- **release-readiness** -- the checklist that currently lives in
  one senior engineer's head, two days before every release.

(Others worth a Skill, not covered today: architecture-review,
jira-ticket-refinement, security-assessment, customer-onboarding,
weekly-business-report, meeting-follow-up, postmortem-generator.)

## One non-developer example

```
Without Skill:

"Summarize this meeting."
```

```
With engineering-meeting/:

Decisions
Action Items       Owner   Due Date
Open Questions
Technical Risks
Architecture Changes
Follow-ups
```

Tools/MCP could then take that output and file the Jira issues or
post the summary -- access, downstream of procedure.

```
PROMPT ENGINEERING

"Please remember all the things
I explained yesterday."
```


[09] THE POINT
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
$ _
```
