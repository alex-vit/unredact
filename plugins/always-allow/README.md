# always-allow

Promote session-approved permissions to your global `~/.claude/settings.json` so you don't have to re-approve them in every project.

```
/always-allow           # scan local permissions, pick which to promote
/always-allow WebSearch # promote a specific pattern directly
```

Auto-generalizes overly specific entries (e.g. `Bash(git push --force-with-lease origin master)` becomes `Bash(git push *)`), deduplicates, and skips anything already global.

## Install

```
/plugin install always-allow@alexv-claude
```
