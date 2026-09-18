# Presenter notes

Your monitor only. `WORKSHOP.md` is the one file the room sees.

The whole talk is **the same prompt, three times**:

```
[02]  no Skill        -> it guesses big
[05]  v1, by hand     -> the small table I asked for
[07]  v2, full Skill  -> web report opens in Chromium
```

## Open it

```
nvim -S presenter.vim WORKSHOP.md    # shared screen
nvim NOTES.md                        # your screen
cd demo                              # the terminal, shared
```

In the presenter: `Space` next section, `Backspace` back. One section
on screen at a time; it opens on the title, and `Backspace` on [00]
goes back to it.

## The three commands

```
../scripts/reset.sh              # no Skill, empty output/
../scripts/claude.sh             # start Claude (clears the screen)
../scripts/install-skill.sh v2   # the full Skill, for [07]
```

**Always restart Claude after installing or editing a Skill.** It's
read from disk, not from the conversation.

Only `claude.sh` starts Claude. Plain `claude` loads your personal
skills, the built-in ones, Artifact and the whole repo, and the demo
falls apart. If you see it exploring outside `demo/` or mentioning
`skill-source`, that's what happened: exit and start again properly.

## Before the talk

```
cd demo
../scripts/reset.sh
../scripts/preflight.sh     # all [ok], warms up the Garmin server
```

Close stray Chromium windows. Rehearse all three runs the day before;
Garmin tokens expire.

## [00]-[01] Agenda, what a Skill is

Ten seconds on the agenda. The three layers are a preview, not the
argument. Let it feel under-explained.

## [02] No Skill

Run the prompt and let it go. Don't help it. It takes about a minute
and dumps a long markdown report nobody asked for, over a week it
picked itself (Thu-Wed, where v2 uses Mon-Sun). "Which days?" was one
of the guesses.

It may ask permission to run date math. Approve it: "now it wants to
run code to work out what 'last week' means".

End on "What I actually wanted". That's the spec for [04].

## [03] Anatomy

Three things: it's a folder with `SKILL.md` in `.claude/skills/`, the
frontmatter says `name` and `description`, and the description is
what gets it picked. Nothing else yet.

## [04] Build one by hand

Type it in the terminal, don't read it off the screen. Narrate one
line per number: which days, which calls, what shape, missing values,
the boundary.

A typo in the frontmatter breaks discovery. If typing goes wrong:
`../scripts/install-skill.sh v1`, then restart.

## [05] Test it, fix it

Same prompt (about 20 s), then "my last 3 days" to show the parameter.

The fix is the Day column: it prints `2026-09-14` because step 3
never says what a day looks like. Add one line, restart, rerun:

```
   Day column: weekday and day number, like "Mon 14".
```

Same prompt twice gives the same table, so don't promise a random
bug. If the run does go wrong on its own, fix that instead.

## [06] MCP vs Skill

They just watched the Skill use 2 of the MCP's tools and ignore the
rest. "Isn't a Skill just a big prompt?" - a prompt is one message you
retype; a Skill is a file that gets picked automatically, brings
references and scripts, and is versioned. [07] shows that.

## [07] Level up

`install-skill.sh v2` replaces v1 in the same folder: same name,
version 2. Never both at once.

Show the tree, one line per file, then run. About 3 minutes. When
Chromium opens: the big number, hover a chart, hover a yellow `!` in
the notable-days grid, then the DATA / OBSERVATION / INTERPRETATION
cards.

The PDF ("Now give me that as a PDF, with charts.") only if asked.

## [08] Why the extra files

Both stories on screen are real:

- The model wrote "Saturday" for runs the data put on Sunday. The
  chart was right. The fix was one line in
  `interpretation-guidelines.md`.
- 11 minutes -> 3: the first version fetched 4 weeks of per-day data
  (85 calls). Asking for 7 days and Garmin's summary tools: 22 calls.

## [09]-[10] Patterns, the point

Speed round; cut this first if you're late. Then let the closing
lines sit. `$ exit` is the ending.

## If something breaks

- **MCP won't connect** (`/mcp`): check `~/.garminconnect` and
  `~/lab/garmin_mcp`. For [07] fall back to
  `../scripts/offline-report.sh` (synthetic data, opens the page).
- **"Unknown skill"** or the old version runs: you didn't restart.
- **Chromium doesn't open:** `chromium output/weekly-report.html`.
- **The pane closes:** you sourced a script with a leading dot. Open
  a new pane.
- **Running long:** cut [09], then the fix in [05], then shorten the
  page tour.
