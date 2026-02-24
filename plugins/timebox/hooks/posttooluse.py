#!/usr/bin/env python3
"""PostToolUse hook for timebox plugin.

Checks elapsed time against the active timebox and injects system messages
at milestone thresholds (50%, 75%, 100%, and repeating reminders after).
"""

import json
import os
import sys
import time

STATE_PATH = os.path.expanduser("~/.claude/timebox.json")


def read_state():
    """Read timebox state file. Returns None if not active."""
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError, OSError):
        return None


def write_state(state):
    """Write updated state back to file."""
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)


def main():
    try:
        state = read_state()
        if state is None:
            sys.exit(0)

        start = state.get("start_epoch", 0)
        duration = state.get("duration_minutes", 0)
        last_milestone = state.get("last_milestone", 0)

        if duration <= 0:
            sys.exit(0)

        now = int(time.time())
        elapsed_s = now - start
        duration_s = duration * 60
        pct = (elapsed_s / duration_s) * 100
        remaining_m = max(0, (duration_s - elapsed_s) / 60)

        message = None
        new_milestone = last_milestone

        if pct >= 100:
            # Past deadline — remind every 60s
            last_remind = state.get("last_expire_remind", 0)
            if now - last_remind >= 60:
                over_m = (elapsed_s - duration_s) / 60
                message = (
                    f"TIMEBOX EXPIRED ({over_m:.0f}m over). "
                    f"Deliver what you have NOW. Summarize done/remaining and stop."
                )
                state["last_expire_remind"] = now
                new_milestone = 100
        elif pct >= 75 and last_milestone < 75:
            message = (
                f"TIMEBOX 75% ({remaining_m:.0f}m left). "
                f"Start wrapping up. No new work items — finish current work, "
                f"commit, and prepare summary."
            )
            new_milestone = 75
        elif pct >= 50 and last_milestone < 50:
            message = (
                f"TIMEBOX 50% ({remaining_m:.0f}m left). "
                f"Check progress against plan. Cut anything that won't fit "
                f"in the remaining time."
            )
            new_milestone = 50

        if message:
            state["last_milestone"] = new_milestone
            write_state(state)
            print(json.dumps({"systemMessage": message}))

        sys.exit(0)

    except Exception:
        # Never crash, never block tool execution
        sys.exit(0)


if __name__ == "__main__":
    main()
