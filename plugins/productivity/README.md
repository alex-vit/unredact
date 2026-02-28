# productivity

Keep dev notes and manage personal tasks in one skill. Sets up and maintains `notes/` directories per project, tracks decisions/TODOs/progress per feature, and manages cross-project tasks, reminders, and recurring routines in a personal docket.

Works in the background — picks up on decisions, deadlines, and action items from conversation. Proactively creates `notes/` in projects that lack one. Reads your docket at session start, executes recurring routines, and keeps things tidy.

Configurable via `~/.claude/squire.json` for docket location and recurring routines. Additional commands: `/productivity status`, `/productivity retry <routine>`, `/productivity clean`.

## Install

```
/plugin install productivity@alexv-claude
```
