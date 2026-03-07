#!/bin/bash
# Re-index Claude Code session history for semantic search.
# Uses content_hash to skip unchanged files -- safe to run frequently.
set -euo pipefail

LLM="$HOME/.local/bin/llm"
PROJECTS_DIR="$HOME/.claude/projects"
MODEL="sentence-transformers/all-MiniLM-L6-v2"

echo "Indexing sessions from $PROJECTS_DIR ..."
"$LLM" embed-multi sessions --files "$PROJECTS_DIR" '**/*.jsonl' -m "$MODEL"
echo "Done."
