#!/usr/bin/env bash
# Starts Claude Code inside demo/, the "empty project" of the talk.
#
# Everything the session needs is passed on the command line, never
# written into demo/: the agent can read any file in its working
# folder, and a rehearsal read demo/.claude/settings.json, saw the
# allow-list naming generate_html.py and open_in_chrome.sh, and
# hand-built an HTML report during the "no Skill" run. So demo/ holds
# the MCP config and nothing else.
#
#   - Skills:  demo/.claude/skills/ only, and none at all while the
#              folder is empty (built-in skills like dataviz would
#              otherwise steer the no-Skill run towards charts)
#   - Denied:  the Artifact tools and the web, so the no-Skill run
#              can't publish a designed page to claude.ai (it did,
#              with real health data) and nothing leaves the laptop
#   - MCP:     demo/.mcp.json (the real Garmin MCP server)
#   - Rules:   below, plus scripts/skill-guard.sh
# Extra arguments are passed through to claude (e.g. -p "...").
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/claude.sh" >&2
  return 1
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="$ROOT_DIR/demo"
SKILL_DIR="$DEMO_DIR/.claude/skills/garmin-weekly-performance-report"
cd "$DEMO_DIR"

# The Garmin MCP server starts uv and logs in to Garmin Connect; from
# cold that has taken more than Claude Code's default 30s and failed
# with CONNECT_TIMEOUT. Give it room.
export MCP_TIMEOUT="${MCP_TIMEOUT:-90000}"

SETTINGS="$(cat <<JSON
{
  "claudeMdExcludes": ["$HOME/.claude/CLAUDE.md"],
  "permissions": {
    "allow": [
      "mcp__garmin__get_activities_by_date",
      "mcp__garmin__get_sleep_summary",
      "mcp__garmin__get_stats",
      "mcp__garmin__get_training_readiness",
      "mcp__garmin__get_user_profile",
      "Bash(python3 .claude/skills/garmin-weekly-performance-report/scripts/generate_html.py:*)",
      "Bash(.venv/bin/python .claude/skills/garmin-weekly-performance-report/scripts/generate_charts.py:*)",
      "Bash(.venv/bin/python .claude/skills/garmin-weekly-performance-report/scripts/generate_pdf.py:*)",
      "Bash(.claude/skills/garmin-weekly-performance-report/scripts/open_in_chrome.sh:*)",
      "Edit(./output/**)"
    ],
    "deny": [
      "Read(../**)",
      "Artifact",
      "ArtifactComments",
      "ArtifactData",
      "WebFetch",
      "WebSearch"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          { "type": "command", "command": "$ROOT_DIR/scripts/skill-guard.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
JSON
)"

NO_SKILLS=()
if [ ! -d "$SKILL_DIR" ]; then
  # Nothing installed yet: turn skills off entirely, so not even the
  # names and descriptions of Claude Code's built-in skills are in
  # play during [02].
  NO_SKILLS=(--disable-slash-commands)
fi

exec claude \
  --setting-sources project,local \
  --settings "$SETTINGS" \
  --mcp-config "$DEMO_DIR/.mcp.json" \
  --strict-mcp-config \
  "${NO_SKILLS[@]}" \
  "$@"
