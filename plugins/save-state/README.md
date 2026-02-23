# save-state

Session state checkpoint — snapshot where you are so a future session can pick up.

When a session ends, the "where was I" knowledge vanishes. `/save-state` captures your current position, open questions, and unfinished work into a structured file that the next session can load to resume seamlessly.

State files live in `.claude/save-state/` per project. Loaded files are archived automatically.

## Install

```
/plugin install save-state@alexv-claude
```
