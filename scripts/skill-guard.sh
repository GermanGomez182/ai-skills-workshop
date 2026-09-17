#!/usr/bin/env bash
# PreToolUse hook on the Skill tool for the demo project: only the
# Skill we install ourselves may run. Claude Code ships built-in
# skills (dataviz, artifact-design, ...) and a rehearsal watched the
# agent use them to hand-build a designed report during the "no
# Skill" run -- stealing the payoff and making the comparison
# meaningless. Denying by hook survives new built-in skills.
#
# Lives outside demo/ on purpose: the agent can't read it, so the
# denial tells it nothing about what the workshop installs later.
set -euo pipefail

OURS="garmin-weekly-performance-report"
SKILL="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("skill",""))')"

if [ "$SKILL" = "$OURS" ]; then
  exit 0
fi

echo "Skills are not available in this project." >&2
exit 2
