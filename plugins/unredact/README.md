# unredact

Restores per-tool-call visibility that Claude Code [removed in v2.1.20](https://symmetrybreak.ing/blog/claude-code-is-being-dumbed-down/).

Claude Code used to show what it was doing — which files it read, what it searched for, what commands it ran. Now it collapses everything into useless summaries like "Read 3 files". This plugin brings that visibility back, printing a one-line summary after each tool call:

```
⏺ Searched for 1 pattern, read 1 file (ctrl+o to expand)
  ⎿  PostToolUse:Glob says: **/* — 46 files
  ⎿  PostToolUse:Read says: README.md — 52 lines
```

## Install

```
/plugin install unredact@alexv-claude
```

## Supported tools

| Tool | Example output |
|------|---------------|
| Read | `package.json — 31 lines` |
| Grep | `"TODO" — 5 files` |
| Glob | `**/*.ts — 12 files` |
| Write | `config.json — 8 lines` |
| Bash | `git status` (uses description, falls back to command) |
| Task | `explore auth flow` |
| NotebookEdit | `analysis.ipynb` |

Other tools (MCP, ToolSearch, etc.) are silently skipped to avoid noise.

## Configuration

### Disable globally

```bash
export UNREDACT_ENABLED=0
```

### Disable per-project

Create `.claude/unredact.local.json`:

```json
{
  "enabled": false
}
```
