# Presenter notes

Open this in a **separate nvim instance, on a monitor you are not
sharing.** `WORKSHOP.md` is the only file that should ever be on
the shared screen -- it has zero comments and zero private text by
design. Nothing in this file is safe to mirror.

Sections below match `WORKSHOP.md`'s `[NN]` markers. Jump the same
way: `/\[05\]`.

---

## Two-monitor setup

- Monitor A (shared / mirrored): `nvim WORKSHOP.md`
- Monitor B (private): `nvim NOTES.md`
- Terminal for actually running demo commands: wherever you like,
  but if it's on Monitor A, remember the audience sees every
  keystroke, including typos and `cd` history. Consider a third
  pane on Monitor B for anything you don't want narrated live
  (e.g. staging the skill directory before [02]).

---

## [00] AGENDA

Ten seconds, don't over-explain the agenda. Move on.

## [01] WTF IS A SKILL?

This is a preview, not the argument -- the argument is the next
50 minutes. Let it feel under-explained on purpose. It lands
harder the second time, at the close in [09].

## [02] WITHOUT SKILL

Before this section:

```
./scripts/demo-hide-skill.sh
```

This moves `.claude/skills/garmin-weekly-performance-report/` to
`.demo-backup/garmin-weekly-performance-report/` and refuses to
run twice (it errors if a backup already exists, so you can't
accidentally clobber it).

**Then exit and restart Claude Code in this directory, before
running the [02] prompt.** Tested, don't skip this: Skills are
discovered when a session starts, not hot-reloaded mid-session --
adding or removing `.claude/skills/garmin-weekly-performance-report/`
while a session is already running does nothing until the next
session start, regardless of what the docs say about watching for
changes. (That watching applies to editing an *already-registered*
skill's files, not to a directory appearing or disappearing.)

This -- a plain `skills/` folder at repo root instead of
`.claude/skills/` -- is also the exact bug that ate 10 minutes the
first time this was rehearsed for real: Claude Code never scanned
it, so the "with skill" run behaved like "without skill." Only
`.claude/skills/` counts, and only at session start.

If you want a sanity check after restarting: ask "what skills do
you have available?" and confirm garmin-weekly-performance-report
isn't in the answer.

Restore it before [04]:

```
./scripts/demo-restore-skill.sh
```

**Restart Claude Code again** before running the [04] prompt, same
reason. This is the same pair of scripts (and the same restart
habit) you'll use again around [06] -- learn it once. Don't fake
the terminal output if something isn't ready (MCP down, script
fails) -- say so and move on.

Turning the restart into a beat instead of a chore: it's a real
demonstration that the Skill lives on disk, not in the
conversation. Nothing about *this chat* changed between runs --
only what's sitting in `.claude/skills/` did.

Run the demo prompt live, ask nothing, let the agent's questions
happen. Then talk through the checklist out loud (it's printed on
screen too, so you're not reading anything the audience can't
see):

- follow-up questions asked
- tool calls made
- manual instructions you had to supply
- missing requirements exposed
- time to result
- format compliance
- consistency (would you get the same shape twice in a row?)

Do NOT claim this proves Skills reduce token usage. That's not the
point of the talk and it isn't measured rigorously here. If asked,
say token counting is a curiosity, not a metric this talk is
making claims about.

If you want real numbers on record afterward (not during the
talk), fill `demo/without-skill.md` from memory right after this
section ends, while it's fresh -- on Monitor B, not live.

## [03] MCP VS SKILL

If someone asks "isn't a Skill just a big prompt" -- answer here,
don't defer it. A Skill can hold instructions, procedures,
references, examples, templates, and scripts. A prompt is one
message. Point back at the file tree in [04]/[05] as the proof.

## [04] WITH SKILL

Same prompt as [02], character for character. If you catch
yourself improving the wording, stop -- you'd be demoing a better
prompt, not a Skill.

After it runs, narrate the same seven-item checklist from [02]
against this run. That spoken comparison IS the demo. Don't retype
it into a file live -- it kills the pacing and there's nothing to
gain from watching you type into a table.

If the demo goes badly (agent still asks something, misses a
threshold, whatever): say so. That's a better teaching moment than
a smooth fake one. Skills failing loudly when they're wrong is the
correct behavior, not an embarrassment.

Fill `demo/with-skill.md` and `demo/comparison.md` afterward, on
Monitor B or after the talk, if you want the numbers on record.

## [05] INSPECT THE SKILL

Actually do this. Stop presenting, open the real file. You're now
inside the object you were describing a minute ago -- that
transition is the whole reason this format beats slides. Take your
time. Walk `metrics.md` and `interpretation-guidelines.md` too if
the room has appetite for it.

## [06] BUILD ONE

This section rebuilds the exact same Skill you already used in
[04] and inspected in [05] -- from scratch, by copy-paste, not from
memory. Do not try to compose SKILL.md's prose live; you will
either run long or write something worse than what's already
written. The whole point of prepared fragments is that the *typing*
risk is gone and only the *narration* is live.

**Setup, right before the section starts** (same pair of scripts as
[02]):

```
./scripts/demo-hide-skill.sh
```

`.claude/skills/` is empty again. **Restart Claude Code now** (same
rule as [02] -- skills are discovered at session start, not
hot-reloaded), before you touch a single file. Building the whole
thing and only restarting at the end would mean testing against a
session that still thinks the old Skill exists.

The original is safe at
`.demo-backup/garmin-weekly-performance-report/`.

**The build, in order.** Fragments live in `demo/build-along/` and
are meant to be pulled in with nvim's `:r` (read-file-into-buffer),
not retyped. After each `:r`, hit `G` (go to end of buffer) before
the next one so they land in the right place; don't sweat exact
blank-line spacing, nobody's diffing this live.

```
$ mkdir -p .claude/skills/garmin-weekly-performance-report
$ touch .claude/skills/garmin-weekly-performance-report/SKILL.md
$ nvim .claude/skills/garmin-weekly-performance-report/SKILL.md
```

1. `:r demo/build-along/01-job-and-trigger.md`
   -- frontmatter, the job, the trigger phrases. Say why the
   `description:` field matters (it's what [06]'s progressive
   disclosure bit is about, coming up next).

2. `:r demo/build-along/02-period-and-data.md`
   -- period, comparison windows, what to pull, "don't fabricate."

3. Save and quit SKILL.md for a moment. Bring in the reference
   files wholesale -- these aren't typed live either, they're
   copied straight from the backup, same as the scripts will be:

   ```
   $ cp .demo-backup/garmin-weekly-performance-report/metrics.md \
        .claude/skills/garmin-weekly-performance-report/metrics.md
   $ cp .demo-backup/garmin-weekly-performance-report/report-template.md \
        .claude/skills/garmin-weekly-performance-report/report-template.md
   $ cp .demo-backup/garmin-weekly-performance-report/interpretation-guidelines.md \
        .claude/skills/garmin-weekly-performance-report/interpretation-guidelines.md
   ```

   Open `interpretation-guidelines.md` briefly and point at the
   DATA/OBSERVATION/INTERPRETATION example -- this is "add examples"
   in the progression, and you already have a real one on disk.

4. Back in `SKILL.md`:
   `:r demo/build-along/03-how-to-build-and-charts.md`
   -- this is the step that actually points at metrics.md,
   report-template.md, interpretation-guidelines.md, and the
   scripts. It's the wiring, not just a pile of files.

5. `:r demo/build-along/04-boundaries.md`
   -- "define what not to do." Read one or two bullets out loud.

6. Scripts, copied wholesale, not typed -- chart/PDF code isn't
   something you compose live any more than the reference docs are:

   ```
   $ mkdir .claude/skills/garmin-weekly-performance-report/scripts
   $ cp .demo-backup/garmin-weekly-performance-report/scripts/*.py \
        .claude/skills/garmin-weekly-performance-report/scripts/
   ```

7. `:r demo/build-along/05-files-in-this-skill.md`
   -- closing section, "iterate" as an explicit habit, not a
   one-time step. Save.

8. **Restart Claude Code** -- the Skill directory now exists again,
   but this session's client only saw it missing. Same rule as
   every other switch in this talk.

9. **Test.** Run the prompt from [02]/[04] again in the new session.
   It should behave the same as [04] -- if it doesn't, that's a
   real, live "iterate" moment, not a script failure.

**If you're behind schedule when you reach [06]:** skip straight to

```
./scripts/demo-restore-skill.sh
```

then restart Claude Code, and walk the finished
`.claude/skills/garmin-weekly-performance-report/` directory
instead of doing the live build. This is a legitimate,
pre-planned fallback, not a failure -- use it decisively rather than
rushing the live-coding and running even further behind.

**If the live build finishes normally:** you don't need to run
`demo-restore-skill.sh` at all -- what you just built by hand *is*
the real thing, byte-for-byte. You still need the restart from step
8 before it's usable in [07].

## [07] RUN IT

`SKILL.md` only generates a PDF "if the user wants a PDF" -- on
purpose, so it doesn't produce files nobody asked for. The vague
prompt from [02]/[04] never asks for one, so [04] correctly ends
with a text report, not a file. Don't read that as a gap live --
say it out loud as intentional, then ask for the file:

```
Now give me that as a PDF, with charts.
```

That's the actual payoff of this section: a real request produces
a real, polished deliverable, still governed by the same Skill.

Prefer live Garmin MCP data here if it's working. Fallback:

```
./scripts/generate-sample-report.sh
```

That script's report text is rule-based (thresholds and templated
phrasing), not the model actually reasoning through
`interpretation-guidelines.md`. Say so if anyone opens the PDF and
asks why the language feels flatter than the live demo's. It's a
rehearsal/fallback tool, not a stand-in for the real thing.

## [08] OTHER PATTERNS

Fast montage, on purpose. Don't build the AWS example live unless
you're ahead of schedule -- it's there to show the pattern
generalizes past fitness data, not to be a second full demo.

If you're short on time, this whole section can shrink to: the AWS
before/after joke, and one of the three bullet Skills. Cut the
meeting example first if something has to go.

## [09] THE POINT

Let the closing lines sit. Don't add anything after
`Don't teach the AI the same thing twice.` -- the `$ _` is the
actual ending, not a segue into more talking.

---

## If something breaks

- Garmin MCP unreachable: switch to
  `./scripts/generate-sample-report.sh` for [07], and for [02]/[04]
  just talk through what *would* happen using this file's
  checklist -- don't fake tool output on the shared screen.
- Skill directory missing when you meant to restore it before
  [04]: run `./scripts/demo-restore-skill.sh`. If that also fails
  (no backup found -- e.g. you hid it twice by hand), it's still
  committed in git: `git checkout -- .claude/skills/garmin-weekly-performance-report`
  gets you back to the last commit's version.
- Running long: cut in this order -- [08] montage, [06] live
  edit-run-fix loop, [07] live MCP run (use the offline script
  instead).
