# AI Skills Workshop

A local, terminal-first workshop about AI Skills: what they are,
why they're not "just a prompt," and why they're not competing
with MCP either.

## What this demonstrates

The same agent, the same MCP access, the same prompt -- run once
without a Skill and once with one. The difference is the entire
talk.

Three ideas the audience should leave with:

```
MODEL        knows things
MCP / TOOLS  can do things
SKILLS       know how WE do things
```

And the closing line:

```
Don't teach the AI
the same thing twice.
```

## Project structure

```
skills-workshop/
|
+-- README.md
+-- WORKSHOP.md              <- the talk. Only file on the shared screen.
+-- NOTES.md                  <- presenter notes. Never shared, never mirrored.
+-- WORKSHOP-SLIDES.md        <- optional Marp export of the same content
|
+-- skills/
|   +-- garmin-weekly-performance-report/
|       +-- SKILL.md
|       +-- metrics.md
|       +-- report-template.md
|       +-- interpretation-guidelines.md
|       +-- scripts/
|           +-- generate_charts.py
|           +-- generate_pdf.py
|
+-- demo/                     <- rehearsal worksheets, not shown live
|   +-- prompts.md
|   +-- without-skill.md
|   +-- with-skill.md
|   +-- comparison.md
|   +-- build-along/          <- fragments pasted live in [06], see NOTES.md
|
+-- sample-data/
|   +-- sample-garmin-week.json   <- SYNTHETIC DEMO DATA, 4 weeks
|
+-- output/                   <- generated reports land here (gitignored content)
|
+-- scripts/
    +-- run-demo.sh
    +-- generate-sample-report.sh
    +-- demo-hide-skill.sh    <- stages the "no skill yet" state for [02]/[06]
    +-- demo-restore-skill.sh <- undoes it
```

## How to open the workshop

This is built for a **two-screen setup**, because you're mirroring
your whole laptop rather than using a presenter-view tool. Anything
open on the shared screen is visible to the room -- so `WORKSHOP.md`
is the only file meant to ever be there, and it has zero hidden
text: no comments, no fill-in-the-blank tables, nothing you
wouldn't want read verbatim off the projector.

```
# shared screen
$ nvim WORKSHOP.md

# your monitor / second device
$ nvim NOTES.md
```

Then `j j j` down through `WORKSHOP.md`. Section markers like
`[04]` are grep/search-friendly, and `NOTES.md` uses the same
numbering so you can jump both in lockstep:

```
/\[05\]
```

`NOTES.md` has the mechanics (when to stage/restore the Skill
directory, what to say if a demo misbehaves, what to cut if you're
running long). It is not meant to be summarized on screen -- if
you don't have a second monitor available, read it beforehand and
rely on `WORKSHOP.md`'s own structure to carry you live.

Skim without nvim:

```
$ bat WORKSHOP.md
```

## How to run the synthetic demo

The live demo depends on a Garmin MCP connection. Since that may
not always be available while rehearsing, `sample-data/` has 4
weeks of clearly-labeled synthetic data with a deliberate story
built in (training load climbs, sleep and recovery dip in the most
recent week) so the "notable changes" and "4-week context"
sections have something real to say.

To generate the charts + PDF from that synthetic data, offline,
with no agent involved:

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ ./scripts/generate-sample-report.sh
```

Output lands in `output/weekly-report.pdf` and `output/charts/`.

This script computes the DATA and OBSERVATION layers the same way
the Skill's rules require, but it does **not** attempt real
interpretation the way the agent does when it has actually read
`interpretation-guidelines.md`. Treat it as a rehearsal tool and a
fallback, not as a stand-in for the live demo.

`scripts/run-demo.sh` is a presenter's sanity check: it confirms
the Skill directory is where you expect, prints the demo prompts,
and lists the beats of the talk so you're not searching for them
mid-sentence.

## How Garmin MCP would replace the synthetic data

In the real demo, the agent doesn't read `sample-garmin-week.json`
at all -- it calls the Garmin MCP server directly (activities,
sleep, HRV, stress, body battery, training readiness, etc.) and
the Skill tells it what to do with the results. The synthetic file
exists purely so this repo is rehearsable without a live Garmin
Connect account in the loop. Swapping real MCP data in requires no
changes to the Skill itself -- that's the point of separating
"how to get the data" (MCP) from "what to do with it" (the Skill).

## How to create the PDF

Same script as above, or run the two steps by hand against any
Garmin-shaped JSON file matching the schema documented at the top
of `generate_charts.py`:

```
$ python3 skills/garmin-weekly-performance-report/scripts/generate_charts.py \
    --input sample-data/sample-garmin-week.json \
    --output-dir output/charts

$ python3 skills/garmin-weekly-performance-report/scripts/generate_pdf.py \
    --input sample-data/sample-garmin-week.json \
    --charts-dir output/charts \
    --output output/weekly-report.pdf
```

Style is deliberately plain: grayscale, monospace, dense. Not a
wellness app.
