# AI Skills Workshop

A terminal-first workshop about AI Skills: what they are, how to
write one, and why they're not "just a prompt" or a replacement for
MCP.

```
MODEL        knows things
MCP / TOOLS  can do things
SKILLS       know how WE do things
```

## The talk in one line

The same prompt, three times, against a real Garmin account:

```
Create a report about my last week.
```

1. **No Skill** -- the agent asks, or guesses big.
2. **v1, typed live** -- a 19-line `SKILL.md`: resting HR and sleep
   score per day, one table.
3. **v2, the full Skill** -- references, scripts, and a dark-mode web
   report that opens in the browser.

Complexity only goes up. `WORKSHOP.md` is what's on the shared
screen; `NOTES.md` is for the presenter only.

## Layout

```
skills-workshop/
+-- WORKSHOP.md               <- the talk (shared screen)
+-- NOTES.md                  <- presenter notes (never shared)
+-- WORKSHOP-SLIDES.md        <- optional Marp version
|
+-- demo/                     <- the "empty project" Claude runs in
|   +-- .mcp.json             <- Garmin MCP server
|   +-- .claude/settings.json <- pre-approved Garmin calls + scripts
|   +-- .claude/skills/       <- installed Skill (untracked)
|   +-- output/               <- reports land here (untracked)
|   +-- .venv -> ../.venv     <- Python for the v2 scripts
|
+-- skill-source/             <- the versions, tracked in git
|   +-- v1/garmin-weekly-performance-report/SKILL.md
|   +-- v2/garmin-weekly-performance-report/
|       +-- SKILL.md, metrics.md, report-template.md,
|       +-- interpretation-guidelines.md
|       +-- scripts/          <- web report, charts, PDF, opener
|
+-- scripts/
|   +-- claude-demo.sh        <- start Claude inside demo/
|   +-- demo-reset.sh         <- no Skill, empty output/
|   +-- install-skill.sh      <- install v1 or v2 into demo/
|   +-- run-demo.sh           <- pre-flight check + the beats
|   +-- generate-sample-report.sh  <- offline v2 report, synthetic data
|
+-- sample-data/              <- one SYNTHETIC week
+-- tests/                    <- pytest for the v2 scripts
```

## Why Claude runs inside `demo/`

Claude Code can't read files outside its working folder. Started
from the repo root, a no-skill run found `skill-source/v2/`, read the
whole Skill and followed it. Started inside `demo/`, it only sees an
almost empty project, so "no Skill" really means no Skill.

`scripts/claude-demo.sh` also loads only `demo/`'s config: no
personal skills, no `~/.claude/CLAUDE.md`, no user hooks, and the
Garmin MCP from `demo/.mcp.json` (the real server at
`~/lab/garmin_mcp`, tokens in `~/.garminconnect`).

Claude Code's own built-in skills (`dataviz`, `artifact-design`,
...) are blocked as well: a PreToolUse hook
(`scripts/only-our-skill.sh`) allows only the installed
`garmin-weekly-performance-report`. Otherwise the "no Skill" run
uses them to hand-build a report, which is neither "no Skill" nor a
fair comparison. `demo/.claude/settings.json` also denies reading
`../**`, so the agent can't wander into the talk's own files.

A Skill is only discovered in `.claude/skills/<name>/SKILL.md`. After
installing or changing one, restart Claude.

## Running it

```
$ uv venv .venv
$ uv pip install --python .venv/bin/python -r requirements-dev.txt

$ cd demo
$ ../scripts/demo-reset.sh
$ ../scripts/run-demo.sh          # pre-flight + the beats
$ ../scripts/claude-demo.sh       # Claude, no Skill

$ ../scripts/install-skill.sh v1  # or type it live
$ ../scripts/install-skill.sh v2
```

Offline, no Garmin, no agent: builds the v2 web report and PDF from
`sample-data/` and opens the page.

```
$ ../scripts/generate-sample-report.sh
```

That report's text is template sentences, not the model's writing.

## Tests

```
$ .venv/bin/pytest
$ .venv/bin/ruff check tests skill-source
```

`tests/test_workshop.py` also checks that the v1 Skill shown in
`WORKSHOP.md` is exactly `skill-source/v1/.../SKILL.md`.
