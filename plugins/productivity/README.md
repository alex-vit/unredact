# productivity

Dev notes, personal tasks, workplace memory, and recurring routines in one plugin.

## Skills

| Skill | Description |
|-------|-------------|
| `productivity` | Dev notes (`notes/` per project) + personal docket (configurable task file) + recurring routines |
| `workplace-memory` | Two-tier memory system — hot cache in `~/.claude/CLAUDE.md`, deep storage in `~/.claude/memory/workplace/`. Decodes people, acronyms, projects, and internal language. |

## Commands

| Command | What it does |
|---------|--------------|
| `/productivity:start` | Initialize workplace memory, bootstrap from task list and connected tools |
| `/productivity:update` | Sync tasks from Linear/GitHub, triage stale items, fill memory gaps |
| `/productivity:update --comprehensive` | Deep scan Slack, email, calendar — flag missed todos, suggest new memories |

## MCP Servers

Adds Google Calendar and Gmail for the `/update --comprehensive` scan.

## Install

```
/plugin install productivity@alexv-claude
```
