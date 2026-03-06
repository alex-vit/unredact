---
name: session-history
description: Search past Claude Code conversation history for keywords, context, and prior solutions. You MUST use this skill whenever the user references previous work ("we discussed", "remember when", "last time", "again", "before", "previous session"), asks about past decisions or approaches, mentions a recurring problem, or wants to reuse something from an earlier session. Also use this proactively when a task feels familiar, when you encounter a problem that was likely solved before, when you need context about what was tried previously, or when you'd otherwise say "I don't have past context" -- because you DO have past context through this skill. Never tell the user you lack memory of prior sessions without searching first.
---

# Session History Search

Search across all past Claude Code sessions stored in `~/.claude/projects/`. Each session is a JSONL file containing user and assistant messages, timestamps, git branches, and more.

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

## Usage

Run the search script from the `scripts/` directory alongside this SKILL.md:

```shell
# Show matching snippets from past conversations (default, most useful)
python3 scripts/search.py "signing key rotation" --project wave --max 5 --show --past

# List matching sessions without snippets (for overview)
python3 scripts/search.py "deploy error" --max 10 --past

# Search all projects (omit --project)
python3 scripts/search.py "webpack config" --max 5 --show --past

# Only recent sessions
python3 scripts/search.py "auth bug" --project wave --after 2026-02-01 --show --past

# Explicitly exclude a session by ID
python3 scripts/search.py "query" --exclude-id abc123-def456 --show
```

The `--past` flag excludes the current session using `CLAUDE_SESSION_ID` from the environment. If the env var isn't set, use `--exclude-id` with the session ID instead.

## How it works

- Scans JSONL session files in `~/.claude/projects/<project>/`
- Extracts text from user and assistant messages (skips system reminders, meta messages, tool calls)
- Scores matches by query word coverage, exact phrase presence, and density
- Shows results centered around the matching text region
- The `--project` filter matches against directory names: "wave" for the monorepo, "claude" for claude config, etc.

## Tips

- Search for specific terms: function names, error messages, ticket IDs, people's names, branch names
- Multi-word queries score higher when all words appear together ("signing key rotation" beats scattered matches)
- Results show the git branch and date to help identify which session/task the match came from
- Use `--show` to scan actual message content; without it you just get file paths and hit counts
- For large result sets, pipe through grep for further filtering
