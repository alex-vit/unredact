---
name: save-state
description: Snapshot session state so a future session can resume where you left off
user-invocable: true
---

# Save State

Capture the current session's position — what you're working on, where you are, what's half-done — into a structured file that a future session can load to resume seamlessly. Notes captures decisions, squire tracks tasks, reflect captures rules — save-state captures *position*.

## Storage

- **State files**: `.claude/save-state/YYYY-MM-DD-<slug>.md` per project
- **Archive**: `.claude/save-state/archive/` for loaded/discarded files
- Separate from notes (different lifecycle — state is ephemeral, notes are durable)

## Commands

- **`/save-state`** — save current session state
- **`/save-state load`** — load and resume from most recent saved state
- **`/save-state list`** — show all saved state files (active and archived)
- **`/save-state discard`** — move a state file to archive without loading

## Saving (`/save-state`)

Assemble state from the current conversation and git status. Create a file in `.claude/save-state/` with today's date and a slug derived from the work being done.

### State file format

```markdown
# <brief title of current work>

Saved: YYYY-MM-DD HH:MM

## Working On
<one-line summary of the task/feature>

## Current Position
<the "you are here" marker — most important section>
<what file/function you were in, what you were about to do next>
<be specific: "was about to implement X in file Y" not "working on feature Z">

## Key Decisions
<decisions made this session that a new session needs to know>
- <decision 1>
- <decision 2>

## Open Questions
<unresolved questions that need answering>
- <question 1>

## Unfinished Work
<what's started but not complete>
- [ ] <item 1>
- [ ] <item 2>

## Files Touched
<files modified or created this session, for quick orientation>
- `path/to/file.ext` — <what was changed>

## Git State
<branch, uncommitted changes, recent commits relevant to current work>

## Related
<links to notes files, squire items, or other context>
```

### Save behavior

1. Review the conversation to identify current work, position, decisions, and open items.
2. Run `git status` and `git log --oneline -5` for git context.
3. Draft the state file.
4. Show the user a summary of what will be saved and confirm before writing.
5. After saving:
   - If the `squire` skill is available, offer to add a meta-item to the docket: `- [ ] Resume: <title> — /save-state load`
   - If there are unfinished items that would make good squire tasks, offer to sync them.

## Loading (`/save-state load`)

1. Find the most recent state file in `.claude/save-state/` (not archive).
2. Read and present a summary to the user.
3. Verify git state still matches (same branch, no unexpected divergence). If it doesn't match, warn the user and explain what changed — don't block the load.
4. Move the file to `.claude/save-state/archive/`.
5. Offer to pick up where the state left off.

## Listing (`/save-state list`)

Show all state files (active first, then archived) with date, title, and one-line summary.

## Discarding (`/save-state discard`)

Move the specified (or most recent) state file to archive without loading. Confirm before discarding.

## Session start

If unloaded state files exist in `.claude/save-state/` (not archive), mention once at the start of the session:

> Saved state from [date]: [title] — `/save-state load` to resume.

Do not auto-load. One mention is enough — don't repeat if the user doesn't act on it.

## Proactive triggers

Propose saving (never save silently) when:
- The session is winding down (user says goodbye, thanks, "that's all", etc.)
- Before a `/clear` if there's meaningful in-progress work
- On a significant context switch (switching to a different feature/project)
- After extended work with no commits (significant unsaved progress)

When proposing, keep it brief: "Want me to save state before we wrap up?"

## Lifecycle

- **Load-and-archive**: loading a state file moves it to archive automatically.
- **Auto-prune**: when running any save-state command, delete archived files older than 14 days.
- **Stale detection**: if an unloaded state file is older than 7 days, flag it once: "Stale saved state from [date] — load or discard?"

## Composability

- **Notes**: link to relevant notes files in the Related section. Do not duplicate notes content.
- **Squire**: offer to sync unfinished items as squire tasks. Add a resume meta-item to docket on save.
- **Reflect**: does not trigger reflect. State snapshots are not lessons.

## Tone

Neutral utility. No persona, no fanfare. Brief confirmations, clear summaries.
