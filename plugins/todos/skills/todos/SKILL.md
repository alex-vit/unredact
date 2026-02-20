---
name: todos
description: View or update personal TODOs, reminders, and deadlines across all work
user-invocable: true
---

# Personal Todos

Track personal tasks, reminders, and deadlines in `~/.claude/todos.md`. This is a single persistent document that spans all projects and sessions — a personal work log and task list.

## Storage

- **File**: `~/.claude/todos.md`
- This file lives outside any repo. It is the source of truth for cross-project personal tasks.
- If the file doesn't exist, create it with the template below.

## Proactive triggers

This skill should be used **proactively** — not only when the user says `/todos`. Check whether `~/.claude/todos.md` should be updated when any of these happen:

- **Task completed**: a feature, bug fix, PR, or deliverable is finished
- **New task surfaces**: user mentions something they need to do later, a follow-up from a PR review, a Slack message that needs action, etc.
- **Switching context**: user moves to a different project or topic — good time to capture where we left off
- **Deadline or reminder mentioned**: user says "by Friday", "next week", "don't forget", "remind me", etc.
- **Session winding down**: if it feels like the session is ending, ask if there's anything to capture
- **User says** "todo", "add a task", "remind me", "track this", "don't forget", or similar

When proactively triggering, **ask the user** before making changes — e.g. "Should I update your personal todos with X?" Keep it lightweight, one line is fine.

## Syncing with other note systems

Before updating, check for other note sources and reconcile:

1. **In-repo notes** (`notes/` directory via the `notes` skill): if available, scan for TODOs and open items. Cross-reference with personal todos — pull in anything that's missing or update status of items that were completed.
2. **CLAUDE.md references**: if `~/.claude/CLAUDE.md` or project-level `CLAUDE.md` mentions note locations, check those too.
3. **Direction of sync**: personal todos is the superset. In-repo notes are project-scoped. When syncing:
   - Items completed in a project's notes → mark done in personal todos
   - New items in personal todos for a specific project → optionally suggest adding to project notes
   - Never delete from personal todos based on project notes — personal todos is the long-lived record

## File format

The document structure is **fluid** — organize by whatever is most useful right now, not by fixed sections. The shape of the file should reflect current priorities.

Examples of structures that might emerge organically:

- A high-pressure project gets its own header at the very top
- Lots of timed things? Maybe `Today`, `Tomorrow`, `This week` headers make sense
- Calm week? A flat list is fine
- Blocked on several things? A `Waiting on` cluster
- Just finished a bunch of stuff? A `Done` section at the bottom for recent completions

### Conventions

- `- [ ]` / `- [x]` for tasks (checkboxes)
- *italicized context* for project/area (e.g. *wave-android*, *data-platform*)
- `due: YYYY-MM-DD`, `done: YYYY-MM-DD` — only when dates matter
- Keep entries terse. One line per task. Details belong in project notes, not here.
- Prune completed items after ~2 weeks — this isn't an archive, it's a working document
- Restructure freely as priorities shift. Headers, groupings, and order should serve the current moment.

## Behavior

- **`/todos`**: read and display the current file. If syncing finds discrepancies, mention them.
- **`/todos add <task>`**: add the task wherever it fits best in the current structure.
- **`/todos done <pattern>`**: mark matching task(s) as done with today's date.
- **`/todos clean`**: prune old done items, tighten up structure.
- **Proactive update**: when triggered proactively, read the file, propose specific changes, and ask for confirmation before writing.
