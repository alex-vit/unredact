# alexv-claude

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugins.

## Setup

```
/plugin marketplace add https://github.com/alex-vit/alexv-claude
```

Then install any plugin below.

## Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| [unredact](plugins/unredact/) | Restores per-tool-call visibility removed in v2.1.20 | `/plugin install unredact@alexv-claude` |
| [always-allow](plugins/always-allow/) | Promote session permissions to global settings | `/plugin install always-allow@alexv-claude` |
| [notes](plugins/notes/) | Per-project development notes and decision log | `/plugin install notes@alexv-claude` |
| [squire](plugins/squire/) | Personal task tracker across all projects | `/plugin install squire@alexv-claude` |
| [reflect](plugins/reflect/) | Captures lessons learned as behavioral rules | `/plugin install reflect@alexv-claude` |
| [save-state](plugins/save-state/) | Session state checkpoint for resuming later | `/plugin install save-state@alexv-claude` |
