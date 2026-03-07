---
name: allow-tool
description: Promote project-local session permissions to global ~/.claude/settings.json
user-invocable: true
---

# Allow Tool

Promote session-approved permissions from the current project's `.claude/settings.local.json` to the global `~/.claude/settings.json` so they apply everywhere.

## Usage

- `/allow-tool` — scan the project's local permissions and choose which to promote
- `/allow-tool <pattern>` — promote a specific pattern directly (e.g. `/allow-tool WebSearch`)

## With argument

1. Use the argument as the pattern. Skip to the **Write** step.

## Without argument (scan & suggest)

### 1. Read candidates

Read `<project>/.claude/settings.local.json` and extract the `permissions.allow` array. If the file doesn't exist or the array is empty, tell the user there are no local permissions to promote and stop.

### 2. Subtract already-global entries

Read both `~/.claude/settings.json` and `~/.claude/settings.local.json`. Remove any candidate that already appears in either global file — match exactly or recognize when a broader wildcard already covers the candidate (e.g. global `Bash(git:*)` covers local `Bash(git push:*)`; global `Edit` covers local `Edit(/src/**/*.ts)`).

If nothing remains after filtering, tell the user all local permissions are already global and stop.

### 3. Generalize

Auto-added entries tend to be overly specific. Generalize by tool type:

**Bash** — extract the command name (first word, or first two for well-known subcommands like `git push`, `go build`, `gh pr`, `npm run`). Produce `Bash(<cmd> *)` as the generalized form. If the candidate already matches this form, keep it unchanged. Legacy `:*` suffix is equivalent to ` *`.

**Edit / Read** — these use gitignore-style path patterns with four root types:

| Prefix | Meaning | Example |
|---|---|---|
| `//` | Absolute filesystem path | `Edit(//tmp/scratch.txt)` |
| `~/` | Relative to home directory | `Edit(~/.claude/settings.json)` |
| `/` | Relative to settings file | `Edit(/src/**/*.ts)` |
| none or `./` | Relative to current directory | `Read(*.env)` |

Generalize specific file paths to their parent directory with `**`: e.g. `Edit(~/.claude/settings.json)` → `Edit(~/.claude/**)`. If the candidate already uses a directory glob, keep it unchanged.

**Other** — `WebSearch`, `WebFetch(domain:...)`, `Skill(...)`, `Task(...)`, MCP tool patterns (`mcp__*`) — keep as-is.

**Deduplicate**: if multiple candidates generalize to the same pattern, collapse them into one entry.

**Examples:**

| Original (local) | Generalized |
|---|---|
| `Bash(git push --force-with-lease origin master)` | `Bash(git push *)` |
| `Bash(go test ./...)` | `Bash(go test *)` |
| `Bash(gh pr create --title "Fix" --body "...")` | `Bash(gh pr *)` |
| `Bash(npm run build)` | `Bash(npm run *)` |
| `Bash(rm -rf /tmp/cache)` | `Bash(rm *)` |
| `Edit(~/.claude/settings.json)` | `Edit(~/.claude/**)` |
| `Edit(/src/components/Button.tsx)` | `Edit(/src/components/**)` |
| `Read(//var/log/app.log)` | `Read(//var/log/**)` |
| `Read(*.env)` | `Read(*.env)` |
| `WebSearch` | `WebSearch` |
| `WebFetch(domain:docs.example.com)` | `WebFetch(domain:docs.example.com)` |

### 4. Present choices

Use `AskUserQuestion` with `multiSelect: true`. Group options by category:

- **Git** — `Bash(git ...)` patterns
- **Go** — `Bash(go ...)` patterns
- **GitHub CLI** — `Bash(gh ...)` patterns
- **File access** — `Edit(...)`, `Read(...)` patterns
- **Web** — `WebSearch`, `WebFetch(...)` patterns
- **MCP** — MCP tool patterns
- **Other** — everything else

Each option's label is the generalized pattern. The description notes what original entries it covers. When generalization changed something, include the original(s) so the user can see what's being broadened.

Example option:

```
label: Bash(git push:*)
description: Covers: "Bash(git push --force-with-lease origin master)", "Bash(git push -u origin feature-x)"
```

### 5. Duplicate check (both modes)

Before writing, confirm the selected pattern (or a broader one covering it) isn't already in `~/.claude/settings.json`. If it is, tell the user and skip that pattern.

### 6. Write

Read `~/.claude/settings.json`, add the selected patterns to `permissions.allow`, and write the file back. Preserve all other keys. Skip any patterns that are already present or covered by existing broader entries.

Report what was added.
