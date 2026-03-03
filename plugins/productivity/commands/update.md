---
description: Sync tasks and refresh memory from your current activity
argument-hint: "[--comprehensive]"
---

# Update Command

Keep your task list and workplace memory current. Two modes:

- **Default:** Sync tasks from external tools, triage stale items, decode tasks for memory gaps
- **`--comprehensive`:** Deep scan Slack, email, calendar — flag missed todos and suggest new memories

## Usage

```
/productivity:update
/productivity:update --comprehensive
```

## Default Mode

### 1. Load Current State

Read config from `~/.claude/squire.json` to find the tasks file.
Read the tasks file and `~/.claude/memory/workplace/` directory.

If workplace memory doesn't exist, suggest `/productivity:start` first.

### 2. Sync Tasks from External Sources

Check for available task sources:
- **Linear** (if MCP available): fetch issues assigned to user (open/in-progress)
- **GitHub Issues** (if in a repo): `gh issue list --assignee=@me`

Compare against the tasks file:

| External task | In tasks file? | Action |
|---------------|----------------|--------|
| Found, not tracked | No match | Offer to add |
| Found, already tracked | Match by title (fuzzy) | Skip |
| In tasks file, not external | No match | Flag as potentially stale |
| Completed externally | Still open in tasks | Offer to mark done |

Present the diff and let the user decide what to add/complete/remove.

### 3. Triage Stale Items

Review the tasks file and flag:
- Tasks with due dates in the past
- Tasks that have sat open for 30+ days with no activity
- Tasks with no context (no person, no project, no link)
- Done items older than 2 weeks (suggest pruning)

Present each for triage: Mark done? Reschedule? Remove? Keep?

### 4. Decode Tasks for Memory Gaps

For each task, attempt to decode all entities using workplace memory:

```
Task: "Follow up on MCP fork PR #94234 — get team input"

Decode:
- MCP fork PR -> ? Not in memory. What is this?
- #94234 -> GitHub PR (can look up)
- "team input" -> which team?
```

Track what's fully decoded vs. what has gaps.

### 5. Fill Memory Gaps

Present unknown terms grouped:

```
I found terms in your tasks I don't have context for:

1. "Manu" (from: "delegated to Manu")
   -> Who is Manu?

2. "WIF" (from: "skip WIF pool refresh")
   -> What does WIF stand for?
```

Add answers to the appropriate memory files and update the hot cache if warranted.

### 6. Report

```
Update complete:
- Tasks: +2 from Linear, 1 completed, 3 triaged
- Memory: 2 gaps filled, 1 person added
- All active tasks decoded ✓
```

## Comprehensive Mode (`--comprehensive`)

Everything in Default Mode, plus a deep scan of recent activity.

### Extra: Scan Activity Sources

Gather from available MCP sources. Skip any that aren't connected.

**Slack:**
- Search recent messages for action items ("I'll", "need to", "follow up", "by Friday")
- Check DMs for commitments made
- Look at active channels for project context

**Google Calendar:**
- List upcoming meetings for the next week
- List recent meetings (last 3 days)
- Note attendees — cross-reference with workplace memory

**Gmail (if available):**
- Search recent sent messages
- Flag commitments made via email

**Linear:**
- Fetch all assigned issues (not just open)
- Check recently completed issues
- Look at comments for action items

### Extra: Flag Missed Todos

Compare activity against the tasks file. Surface action items that aren't tracked:

```
## Possible Missing Tasks

From your recent activity:

1. From Slack (Mar 2):
   "I'll send the updated mockups by Friday"
   -> Add to tasks?

2. Meeting "Android standup" (Mar 3):
   You have a recurring meeting but no related open tasks
   -> Anything to track here?

3. Linear USER-4691 assigned to you, not in tasks file:
   "Implement flashlight feature on ID and selfie photo screens"
   -> Add to tasks?
```

Let the user pick which to add.

### Extra: Suggest New Memories

Surface new entities not in workplace memory:

```
## New People (not in memory)
| Name | Frequency | Context |
|------|-----------|---------|
| Jamie Park | 8 mentions | design reviews, Slack DMs |
| Chris L | 5 mentions | PR reviews |

## New Projects/Topics
| Name | Frequency | Context |
|------|-----------|---------|
| Xender compat | 4 mentions | AAB PR discussions |

## Suggested Cleanup
- **Key rotation** — marked done in tasks. Update project status?
```

Present grouped by confidence. High-confidence offered to add directly; low-confidence asked about.

### Extra: Calendar Prep

If there are meetings in the next 24 hours:

```
## Upcoming Meetings
- **Android standup** (tomorrow 10am) — Eduard, Monica, Alex
  Memory has: Monica (EM), Eduard (Android). All decoded ✓
- **1:1 with Drew** (tomorrow 2pm)
  Memory has: ? Drew not in memory. Who is Drew?
```

Surface unknown attendees for memory capture.

## Notes

- Never auto-add tasks or memories without user confirmation
- External source links are preserved when adding tasks
- Fuzzy matching on task titles handles minor wording differences
- Safe to run frequently — only surfaces new information
- `--comprehensive` is interactive — presents findings for review, doesn't auto-modify
