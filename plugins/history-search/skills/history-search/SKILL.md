---
name: history-search
description: Search past Claude Code conversation history for keywords, context, and prior solutions. You MUST use this skill whenever the user references previous work ("we discussed", "remember when", "last time", "again", "before", "previous session"), asks about past decisions or approaches, mentions a recurring problem, or wants to reuse something from an earlier session. Also use this proactively when a task feels familiar, when you encounter a problem that was likely solved before, when you need context about what was tried previously, or when you'd otherwise say "I don't have past context" -- because you DO have past context through this skill. Never tell the user you lack memory of prior sessions without searching first.
---

# Session History Search

Search across all past Claude Code sessions using semantic embeddings via `llm similar`. Queries are matched by meaning, not just keywords -- describe what you're looking for naturally.

Requires `llm` CLI (`~/.local/bin/llm`) with the `llm-sentence-transformers` plugin and `all-MiniLM-L6-v2` model.

## When to search

The value of this skill is in preventing repeated work and recovering lost context. Search proactively -- don't wait for the user to ask:

- The user references past work ("we did this before", "remember when", "that thing from last week")
- You're starting a task that feels like it was attempted before
- You encounter a problem and suspect a prior session solved it
- The user asks about a decision or approach from a previous conversation
- You'd otherwise tell the user you don't have context from prior sessions

Check these sources in order, since earlier ones are faster and more curated:
1. **MEMORY.md** -- always loaded, check first
2. **Library** (`~/.claude/library/INDEX.md`) -- curated solutions
3. **session-history** (this skill) -- raw conversation history, the full recall

## Search strategy

Semantic search understands meaning, so describe what you're looking for naturally. You don't need exact keywords -- conceptual queries work well.

For example, if the user says "remember that issue with the tray icon not showing up?":
- Works great: `"tray icon not showing up"`, `"systray icon visibility problem"`
- Also works: `"energye tray notification bug"`, `"system tray icon transparent"`

All of these will find relevant sessions because the embeddings capture semantic similarity.

Run 2-3 queries with different phrasings to maximize coverage. Broader conceptual queries and narrower specific queries complement each other.

## Usage

```shell
# Basic search (top 10 results)
python3 $CLAUDE_PLUGIN_ROOT/scripts/history-search.py "signing key rotation"

# Filter by project
python3 $CLAUDE_PLUGIN_ROOT/scripts/history-search.py "deploy error" --project wave

# More results
python3 $CLAUDE_PLUGIN_ROOT/scripts/history-search.py "webpack config" -n 20
```

## Output format

Plain text, one result per block:

```
--- [project] YYYY-MM-DD (uuid8chr) [0.53] ---
<first user message excerpt, up to 800 chars>
```

- `project` — the project directory name (e.g., "wave", "monibright")
- `uuid8chr` — first 8 characters of the session UUID
- `[0.53]` — cosine similarity score (higher = more relevant)

## How it works

- Session JSONL files are embedded at the session level using `sentence-transformers/all-MiniLM-L6-v2`
- `llm similar` finds the closest embeddings by cosine similarity
- The wrapper script reads source JSONL files to extract dates and excerpts (embeddings DB stores no content)
- Re-index with `$CLAUDE_PLUGIN_ROOT/scripts/history-reindex.sh` (incremental -- skips unchanged files)

## Tips

- Natural language queries are the strength: "that time we debugged CI failures" works as well as "CircleCI build error"
- Use `--project` to narrow results when you know which project the conversation was about
- Scores above 0.4 are usually strong matches; below 0.3 are loose associations
- Results are pipe-friendly -- no colors, no ANSI codes
- Re-index periodically to pick up new sessions: `$CLAUDE_PLUGIN_ROOT/scripts/history-reindex.sh`

## Setup

### Prerequisites

```shell
# Install llm CLI via pipx
pipx install llm

# Install the sentence-transformers plugin
~/.local/bin/llm install llm-sentence-transformers

# Download the embedding model (~80MB, runs locally, no API key needed)
~/.local/bin/llm embed -m sentence-transformers/all-MiniLM-L6-v2 -c "test"
```

### Initial indexing

```shell
# Index all session JSONL files (~774 sessions, takes a few minutes first time)
$CLAUDE_PLUGIN_ROOT/scripts/history-reindex.sh
```

### Automatic indexing

A `SessionStart` hook in `~/.claude/settings.json` runs the reindex script at the start of each Claude Code session. This keeps the index up to date incrementally (uses content_hash to skip unchanged files, typically completes in seconds).

### Files

| File | Purpose |
|------|---------|
| `$CLAUDE_PLUGIN_ROOT/scripts/history-search.py` | Search wrapper — parses `llm similar` output, extracts excerpts |
| `$CLAUDE_PLUGIN_ROOT/scripts/history-reindex.sh` | Reindex script — runs `llm embed-multi` incrementally |
| `~/AppData/Roaming/io.datasette.llm/embeddings.db` | Embeddings database (collection: `sessions`) |

## Limitations

- **Session-level granularity**: Embeddings represent entire sessions. If a topic was a small part of a long session, it may not surface. For niche subtopics, fall back to `grep -rl "keyword" ~/.claude/projects/ --include="*.jsonl"` to find exact matches.
- **No content in DB**: The embeddings database stores no session text. Source JSONL files must exist for excerpts to display.
