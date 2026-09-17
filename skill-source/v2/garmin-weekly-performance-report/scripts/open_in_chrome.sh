#!/usr/bin/env bash
# Opens a local report file in a new Chrome window, detached from
# the agent's shell so the browser stays open after the run ends.
# Tries Google Chrome first, then Chromium (what Chrome is built on).
# Usage: open_in_chrome.sh output/weekly-report.html
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  echo "[!!] don't source this, run it: $(basename "${BASH_SOURCE[0]}")" >&2
  return 1
fi

set -euo pipefail

if [ $# -ne 1 ] || [ ! -f "$1" ]; then
  echo "[!!] usage: open_in_chrome.sh <existing-file> (got: ${1:-nothing})" >&2
  exit 1
fi

REPORT="$(realpath "$1")"

for browser in google-chrome-stable google-chrome chromium chromium-browser; do
  if command -v "$browser" >/dev/null; then
    setsid -f "$browser" --new-window "file://$REPORT" >/dev/null 2>&1
    echo "[ok] opened in $browser: $1"
    exit 0
  fi
done

echo "[!!] no Chrome or Chromium found on PATH; open it by hand: $REPORT" >&2
exit 1
