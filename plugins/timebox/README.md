# timebox

Constrain open-ended work to a fixed duration. A PostToolUse hook checks elapsed time and injects system messages at milestones, forcing scope cuts and timely delivery.

## Install

```
/plugin install timebox@alexv-claude
```

## Usage

```
/timebox 15      # start a 15-minute timebox
/timebox stop    # cancel the active timebox
```

## How it works

Starting a timebox writes a state file (`~/.claude/timebox.json`) with the start time and duration. After every tool call, the hook checks elapsed time and injects reminders:

| Milestone | Message |
|-----------|---------|
| 50% | Check progress, cut what won't fit |
| 75% | Start wrapping up, no new work items |
| 100% | Deliver now, summarize done/remaining |
| 100%+ | Repeat reminder every 60 seconds |

The skill also provides behavioral guidance: three-phase workflow (assess → execute → wrap up), incremental delivery, and no rabbit holes.

## State file

`~/.claude/timebox.json`:

```json
{
  "start_epoch": 1708790400,
  "duration_minutes": 15,
  "last_milestone": 0
}
```

Cancelling (`/timebox stop`) removes this file.
