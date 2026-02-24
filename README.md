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
| [productivity](plugins/productivity/) | Dev notes, personal tasks, reminders, and recurring routines | `/plugin install productivity@alexv-claude` |
| [go](plugins/go/) | Go conventions, build patterns, and platform-specific gotchas | `/plugin install go@alexv-claude` |
| [android](plugins/android/) | Android SDK tooling gotchas — emulators, signing, sdkmanager, AVDs | `/plugin install android@alexv-claude` |
| [playwright-headless](plugins/playwright-headless/) | Headless Playwright MCP — browser automation without visible windows | `/plugin install playwright-headless@alexv-claude` |
