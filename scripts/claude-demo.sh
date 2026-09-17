#!/usr/bin/env bash
# Starts Claude Code inside demo/, the "empty project" of the talk,
# with that project's config only:
#   - Skills:  demo/.claude/skills/ (nothing from ~/.claude/skills)
#   - MCP:     demo/.mcp.json (the real Garmin MCP server)
#   - Rules:   demo/.claude/settings.json
# Claude Code can't read outside its working folder, so the agent
# never sees skill-source/ or the workshop notes. Your personal
# skills, hooks and ~/.claude/CLAUDE.md stay out too.
# Extra arguments are passed through to claude (e.g. -p "...").
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this (no leading dot), run it: scripts/claude-demo.sh" >&2
  return 1
fi

set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../demo" && pwd)"
cd "$DEMO_DIR"

exec claude \
  --setting-sources project,local \
  --settings "{\"claudeMdExcludes\":[\"$HOME/.claude/CLAUDE.md\"]}" \
  --mcp-config "$DEMO_DIR/.mcp.json" \
  --strict-mcp-config \
  "$@"
