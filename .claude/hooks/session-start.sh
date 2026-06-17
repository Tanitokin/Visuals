#!/bin/bash
# SessionStart hook: prepare the Manim render environment (web sessions only).
set -uo pipefail

# Only run in Claude Code on the web (remote); skip on local machines.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0
bash setup.sh
