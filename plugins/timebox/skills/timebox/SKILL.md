---
name: timebox
description: Constrain work to a fixed duration — forces scope cuts, incremental delivery, and timely wrap-up
user-invocable: true
---

# Timebox

Constrain the current task to a fixed number of minutes. Forces you to cut scope, deliver incrementally, and wrap up on time.

## Usage

- `/timebox N` — start a timebox of N minutes (e.g. `/timebox 15`)
- `/timebox stop` — cancel the active timebox

## Starting a timebox

If the argument is `stop`, see **Cancellation** below.

Otherwise, parse N as the number of minutes. Run this bash command to create the state file:

```bash
python3 -c "
import json, time, os
path = os.path.expanduser('~/.claude/timebox.json')
state = {'start_epoch': int(time.time()), 'duration_minutes': $DURATION, 'last_milestone': 0}
with open(path, 'w') as f:
    json.dump(state, f)
print('Timebox started: $DURATION minutes')
"
```

Replace `$DURATION` with the user's N value.

## Three-phase workflow

After starting the timer, work in three phases:

1. **Assess (first 10%)** — understand the task, identify what's achievable within the timebox, cut scope aggressively
2. **Execute (next 70%)** — do the work, deliver incrementally, commit partial progress early
3. **Wrap up (final 20%)** — finish current work item, write summary of what was done and what remains, commit

## Behavioral rules while timeboxed

- **Action over analysis.** Don't spend the timebox planning — start producing output immediately.
- **Scope to fit.** If the task won't fit in the remaining time, cut scope now. Deliver something complete over something half-done.
- **Deliver incrementally.** Commit working code early and often. Each commit should leave the codebase in a working state.
- **No rabbit holes.** If something takes longer than expected, stop, note it as a follow-up, and move on.
- **Respect the milestones.** When the hook injects milestone messages, adjust your behavior:
  - **50%** — check progress against plan, cut anything that won't fit
  - **75%** — start wrapping up, no new work items
  - **100%** — deliver what you have now, summarize done/remaining

## Cancellation

When the argument is `stop`:

```bash
rm -f ~/.claude/timebox.json && echo "Timebox cancelled."
```
