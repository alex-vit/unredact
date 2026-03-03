---
description: Initialize the workplace memory system and bootstrap from your task list and connected tools
---

# Start Command

Initialize the workplace memory system. Creates the directory structure, bootstraps knowledge from your task list, and optionally scans connected tools for richer context.

## Instructions

### 1. Read Config

Read `~/.claude/squire.json` to find the tasks file. Default: `./TASKS.md` if no config exists.

### 2. Check What Exists

Check for:
- `~/.claude/memory/workplace/` — deep memory directory
- `~/.claude/CLAUDE.md` — check for a `## Workplace` section (hot cache)

### 3. Create What's Missing

**If `~/.claude/memory/workplace/` doesn't exist:**
```
~/.claude/memory/workplace/
  glossary.md
  people/
  projects/
  context/
    company.md
```

Create each file with the template headers from the workplace-memory skill.

**If `~/.claude/CLAUDE.md` doesn't have a `## Workplace` section:**
Add the section with empty tables (People, Terms, Projects). Place it at the end of the file.

### 4. Bootstrap from Task List

Read the configured tasks file. This is the richest source of workplace language.

For each task item, analyze for:
- **Names** that might be nicknames or shorthand
- **Acronyms** or abbreviations
- **Project references** or codenames
- **Internal terms** or jargon
- **Linear ticket references** (e.g. USER-4691)
- **Slack thread links** — these provide context about who's involved
- **PR references** — these reveal collaborators

**Decode interactively:**

```
I found some terms in your tasks I want to make sure I understand:

1. **GSM** (from: "Store customer upload keystore in GCP Secret Manager")
   -> Google Secret Manager? Or something else?

2. **Manu** (from: "delegated to Manu")
   -> Who is Manu? Full name, role?

3. **babysit PR** (from: "babysit-pr telemetry")
   -> I see this references a skill. What does it do in your workflow?
```

Only ask about terms not already decoded. Group questions — don't ask one at a time for large task lists.

### 5. Optional: Scan Connected Tools

After task list decoding, offer:

```
Want me to scan your connected tools for more context?
- Slack: recent DMs and active channels -> discover people and projects
- Linear: assigned issues -> discover active projects and collaborators
- Google Calendar: upcoming meetings -> discover meeting patterns and attendees

This takes longer but builds richer context. Or we can stick with what we have.
```

**If they choose to scan:**

Gather from available MCP sources:
- **Slack:** Recent messages, frequent DM partners, active channels
- **Linear:** Issues assigned to user, recent activity, team members
- **Google Calendar:** Upcoming meetings, recurring events, attendees
- **Gmail:** Recent sent messages, frequent recipients (if available)

Build a braindump. Present grouped by confidence:
- **Ready to add** (high confidence, seen in multiple sources) -> offer to add directly
- **Needs clarification** -> ask the user
- **Low frequency** -> note for later

### 6. Write Memory Files

From everything gathered:

1. **glossary.md** — all decoded terms, acronyms, nicknames
2. **people/*.md** — profiles for everyone identified
3. **projects/*.md** — active projects with key people and context
4. **context/company.md** — teams, tools, processes discovered
5. **CLAUDE.md hot cache** — top-30 most relevant entries from above

### 7. Report

```
Workplace memory initialized:
- People: X profiles (Y in hot cache)
- Terms: X decoded (Y in hot cache)
- Projects: X tracked
- Deep storage: ~/.claude/memory/workplace/
- Hot cache: ~/.claude/CLAUDE.md ## Workplace

Use /productivity:update to keep things current.
Use /productivity:update --comprehensive for a deep scan of all activity.
```

## Notes

- If memory is already initialized, report the current state and offer to re-bootstrap
- Nicknames are critical — always capture how people are actually referred to
- If an MCP source isn't available, skip it and note the gap
- Don't auto-add anything without user confirmation during bootstrap
- Memory grows organically through natural conversation after bootstrap
