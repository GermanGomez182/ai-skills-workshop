# Presenter notes

Open this in a **separate nvim instance, on a monitor you are not
sharing.** `WORKSHOP.md` is the only file that goes on the shared
screen. Nothing in this file is safe to mirror.

Sections match `WORKSHOP.md`'s `[NN]` markers. Jump with `/\[05\]`.

The whole talk is one idea: **the same prompt, three times.**

```
[02]  no Skill        -> it asks, or guesses big
[05]  v1, by hand     -> the small table I asked for
[07]  v2, full Skill  -> web report opens in Chromium (the win)
```

Complexity only goes up. Nobody sees `metrics.md` or a script
before they have understood a 19-line `SKILL.md`.

---

## Setup

- Monitor A (shared): `nvim WORKSHOP.md` + a terminal **inside
  `demo/`**. Every demo command runs from there.
- Monitor B (private): `nvim NOTES.md`.
- Always start Claude with `../scripts/claude.sh`, never plain
  `claude`. It runs Claude inside `demo/` and passes everything else
  on the command line: the Garmin MCP from `demo/.mcp.json` (your
  real server and tokens), pre-approved Garmin calls and scripts (no
  permission prompts on stage), no personal skills, no
  `~/.claude/CLAUDE.md`.
- `demo/` holds only `.mcp.json`, `output/` and the `.venv` link.
  Settings are *not* written there on purpose: the agent can read
  anything in its working folder, and a rehearsal read
  `demo/.claude/settings.json`, saw the allow-list naming
  `generate_html.py` and `open_in_chrome.sh`, and hand-built an HTML
  report during the "no Skill" run.
- **Built-in skills are off.** Claude Code ships its own
  (`dataviz`, `artifact-design`, ...) and a rehearsal watched the
  no-skill run use them to hand-build a designed report -- so "no
  Skill" wasn't true, and it spent the [07] payoff early. Two
  measures: while no Skill is installed the launcher passes
  `--disable-slash-commands`, so the Skill tool doesn't exist at all
  and not even those descriptions are in context; once one is
  installed, a PreToolUse hook (`scripts/skill-guard.sh`, outside
  `demo/` so the agent can't read it) allows only
  `garmin-weekly-performance-report`. Same rule for all three runs:
  the only difference between them is our Skill.
- `demo/.claude/settings.json` also denies reading `../**`, so the
  agent never asks for `WORKSHOP.md` or these notes on stage.
- Why `demo/` and not the repo root: Claude Code can't read outside
  its working folder. From the repo root, a no-skill rehearsal found
  `skill-source/v2/`, read the whole Skill and followed it -- the
  "no Skill" run wasn't. From `demo/` it can't see `skill-source/`,
  `WORKSHOP.md` or these notes (verified 2026-09-16: Read, `cat`
  and `ls ..` are all blocked).

## Before the talk

```
cd demo
../scripts/reset.sh     # no skills, empty output/
../scripts/preflight.sh       # all [ok]
```

- Commit (or stash) everything. Claude Code shows the agent a short
  `git status`; uncommitted renames like `skill-source/v2/...` gave
  a no-skill rehearsal the path to try. The `demo/` boundary blocked
  it, but don't hand out hints.
- Close every Chromium window. First Chromium launch after boot is
  slow: open and close it once.
- Do the full rehearsal the day before (all three runs). Garmin
  tokens expire; find out at home, not on stage.
- Have `skill-source/v1/garmin-weekly-performance-report/SKILL.md`
  open in a private buffer, in case you want to copy from it.

---

## [00] AGENDA

Ten seconds. "Same prompt, three times" is the only thing to say.

## [01] WTF IS A SKILL?

A preview, not the argument. Let it feel under-explained; it lands
again at [10].

## [02] NO SKILL

Run the prompt and let it go. Don't help it. Whatever it does is
the point:

- asks questions -> "it has to ask, because nobody wrote it down"
- guesses -> "look how much it decided on its own: which metrics,
  which days, the format"

Don't count tool calls or time out loud. One sentence is enough:
"lots of calls, lots of decisions, not what I wanted."

Rehearsal 2026-09-17: 74 s, 17 Garmin calls, and it wrote a long
markdown report to `output/` that nobody asked for. It also picked
its own week (Thu-Wed, a rolling 7 days) where v2 uses Mon-Sun.
Point at that: "which days?" was one of the guesses.

It may stop for **permission prompts** on its date math (`python3
-c ...`, shell loops). Approve them; say "and now it wants to run
code to figure out what 'last week' means".

There are no skills at all in this run, so nothing steers it: what
you see is the model on its own.

If the agent says anything about a Skill or `skill-source`, stop
and check you're in `demo/` and started it with `claude.sh`.

End on the "What I actually wanted" block. That's the spec for [04].

## [03] ANATOMY OF A SKILL

Three ideas, nothing else:

Typically defined by a SKILL.md file containing YAML metadata and Markdown instructions, skills allow agents to load domain-specific procedural knowledge on demand rather than upfront, keeping context windows lean and ensuring consistent, repeatable outputs


1. It's a folder with `SKILL.md`, and it has to be in
   `.claude/skills/`.
2. Frontmatter: `name` + `description`. The description says WHEN.
3. The agent only reads name + description until a request
   matches (progressive disclosure, without saying the words yet).

"We learned that one live": an early version of this repo had the
Skill in `skills/` at the root. Claude never saw it. Tell it if
someone laughs; skip it if not.

## [04] BUILD ONE BY HAND

Type it for real in the terminal on Monitor A (not in
`WORKSHOP.md`). The block in `WORKSHOP.md` is the recap people can
read while you type; scroll to it after.

Narrate while typing, one line per number:

- description: "this is how it gets picked; name the requests"
- 1: which days, and the escape hatch for "last 3 days"
- 2: which calls, and "nothing else" -- that's what keeps it fast
- 3: the shape
- 4: never invent a number
- 5: the boundary

Typos in the frontmatter break discovery. If typing goes badly,
don't fix it live:

```
../scripts/install-skill.sh v1
```

Then exit Claude and restart with `../scripts/claude.sh`.
**Always restart after changing what's installed**; mid-session
discovery has been inconsistent in testing.

## [05] TEST IT, FIX IT

Same prompt, then the "last 3 days" one. Point at the difference
qualitatively (no questions, small, exact shape).

Rehearsal 2026-09-16: last week took about 23 s and 14 calls; last
3 days about 18 s and 6 calls. Both printed exactly the table.

**The planned live fix is real:** in rehearsal the 7-day average
row came out as whole numbers in bold, the 3-day one as `69.7`
without bold. Point at it, then add to step 3:

```
   Averages: whole numbers, no bold.
```

Restart, rerun "last 3 days". Other ideas if there's time:

- add "Sort newest day first." to step 3
- add "Mark sleep scores below 60 with (!)." to step 3

If something genuinely goes wrong in the run (wrong days, extra
text), that's better: fix the line that caused it, live.

## [06] MCP VS SKILL

Now it's concrete: they just watched the Skill pick 2 of the MCP's
tools and ignore the rest. Point back at step 2 of the file.

If someone asks "isn't a Skill just a big prompt?": a prompt is one
message you retype. A Skill is a file that's picked automatically,
can bring references and scripts, and is versioned. [07] shows the
"references and scripts" part.

## [07] LEVEL UP

`install-skill.sh v2` replaces v1 in the same folder: same name,
version 2. Don't install both side by side; they'd both match the
prompt and the agent could pick either.

Show the tree, one sentence per file, then run. It takes about
3 minutes (rehearsal 2026-09-17: 179 s, 22 Garmin calls, no
permission prompts). While it runs, talk through [08]'s first bullet
(references), then come back when Chromium opens.

When the page opens, give it room:

- the big number, then scroll
- hover a chart
- the notable days grid: hover a yellow `!`
- the DATA / OBSERVATION / INTERPRETATION cards

The PDF still exists ("Now give me that as a PDF, with charts."),
but skip it unless someone asks.

## [08] WHY THE EXTRA FILES

The rehearsal stories on screen are real (2026-09-16):

- Saturday/Sunday: the model's prose said the runs were on
  "Saturday, Sep 13"; the data and chart said Sunday. The new check
  is the last bullet of `interpretation-guidelines.md`.
- Eleven minutes -> three: the first version of the full Skill
  fetched 4 weeks of per-day data (85 calls, ~150 KB of raw sleep
  data per night). Asking for 7 days and Garmin's summary tools:
  22 calls, about 3 minutes including building and opening the web
  page.

Keep numbers to those two sentences. If someone wants details:
`skill-source/v2/.../SKILL.md`, "Data to retrieve".

## [09] OTHER PATTERNS

Speed round. Cut this first if you're late.

## [10] THE POINT


Agent skills are modular, reusable packages of instructions, metadata, and optional resources (such as scripts or templates) that give AI agents specialized capabilities for specific tasks. 
---

## If something breaks

- **Garmin MCP won't connect** (`/mcp` shows it failed): check
  `~/.garminconnect` exists and `~/lab/garmin_mcp` is where
  `demo/.mcp.json` expects it. For [07], fall back to
  `../scripts/offline-report.sh` (synthetic data, opens the
  web page). For [02]/[05], talk through what would happen; don't
  fake output.
- **"Unknown skill"** or the old version runs: you didn't restart.
  Exit, `../scripts/claude.sh`, same prompt.
- **Chromium doesn't open:** the page is `output/weekly-report.html`;
  open it by hand with `chromium output/weekly-report.html`.
- **Pane closes when running a script:** you typed a leading dot
  (`. ../scripts/...`). The scripts refuse to be sourced now, but a
  shell that sourced one earlier may still have `set -e` on. Open a
  new pane.
- **Running long:** cut [09], then the live fix in [05], then
  shorten the page tour in [07].
