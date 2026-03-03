---
name: workplace-memory
description: Two-tier memory system for workplace context — decodes shorthand, people, acronyms, projects, and internal language so Claude understands requests like a colleague would. Auto-triggered when encountering unknown terms or people references.
---

# Workplace Memory

Workplace memory makes Claude a collaborator who speaks your internal language.

## The Goal

Transform shorthand into understanding:

```
User: "check with Monica about the selfie screen flash for USER-4691"
              ↓ Claude decodes
"Check with Monica Dumitrescu (Engineering Manager, wave-android) about
 the flashlight feature on ID/selfie photo screens — Linear ticket USER-4691"
```

Without memory, Claude asks clarifying questions. With memory, Claude knows:
- **Monica** -> Monica Dumitrescu, EM for wave-android
- **selfie screen flash** -> USER-4691, flashlight on ID/selfie capture screens
- **USER-4691** -> Linear ticket, assigned to Alex

## Architecture

Two tiers:

```
~/.claude/CLAUDE.md              <- Hot cache (globally loaded, always in context)
~/.claude/memory/workplace/
  glossary.md                    <- Full decoder ring (all terms, all people)
  people/                        <- Individual profiles
  projects/                      <- Project details
  context/                       <- Company, teams, tools, processes
```

### Hot cache (`~/.claude/CLAUDE.md`)

A `## Workplace` section in the global CLAUDE.md. Contains:
- Top ~30 people you interact with most
- ~30 most common acronyms/terms
- Active projects (5-15)
- Goal: cover 90% of daily decoding needs

Format — use tables for compactness:

```markdown
## Workplace

Full details: ~/.claude/memory/workplace/

### People
| Who | Role |
|-----|------|
| **Monica** | Monica Dumitrescu, EM wave-android |
| **Eduard** | Eduard X, Android engineer |

### Terms
| Term | Meaning |
|------|---------|
| GSM | Google Secret Manager |
| AAB | Android App Bundle |
| WIF | Workload Identity Federation |

### Projects
| Name | What |
|------|------|
| **Key rotation** | Customer app signing key rotation (USER-4727) |
```

### Deep storage (`~/.claude/memory/workplace/`)

**glossary.md** — the decoder ring:
```markdown
# Glossary

## Acronyms
| Term | Meaning | Context |
|------|---------|---------|
| GSM | Google Secret Manager | Android CI secrets |
| PSR | Pipeline Status Report | Weekly sales doc |

## Internal Terms
| Term | Meaning |
|------|---------|
| monorepo | wavemm/monorepo on GitHub |
| the incident | #incident-382, signing key leak |

## Nicknames
| Nickname | Person |
|----------|--------|
| Monica | Monica Dumitrescu (EM) |
```

**people/{name}.md** — individual profiles:
```markdown
# Monica Dumitrescu

**Also known as:** Monica
**Role:** Engineering Manager
**Team:** wave-android
**Reports to:** [manager]

## Communication
- Slack, direct style

## Context
- Manages Android team priorities
- Key contact for sprint planning, PR reviews
```

**projects/{name}.md** — project details:
```markdown
# Customer App Signing Key Rotation

**Linear:** USER-4727
**Status:** Active
**Codename:** "key rotation", "the incident"

## Key People
- Alex — lead
- Manu — agent key rotation
- Eduard — AAB PR

## Context
Customer signing key leaked in monorepo. Rotating upload key via Play Console.
```

**context/company.md** — teams, tools, processes:
```markdown
# Company Context

## Tools
| Tool | Used for | Internal name |
|------|----------|---------------|
| Linear | Issue tracking | - |
| Slack | Communication | - |
| GitHub | Code, PRs | "monorepo" |
| Snowflake | Data warehouse | - |

## Teams
| Team | What | Key people |
|------|------|------------|
| wave-android | Android apps | Monica (EM), Eduard, Alex |

## Processes
| Process | What |
|---------|------|
| /approve | PR approval via comment (not gh review) |
| babysit PR | Monitor CI with wave-eng:ci:babysit-pr skill |
```

## Lookup Flow

When processing any user request:

```
1. Check ~/.claude/CLAUDE.md "Workplace" section (hot cache)
   -> Covers 90% of daily decoding

2. If not found -> read ~/.claude/memory/workplace/glossary.md
   -> Full glossary has everyone/everything

3. If richer context needed -> read people/{name}.md or projects/{name}.md
   -> Full profiles, history, relationships

4. If still not found -> ask user
   -> "What does X mean? I'll remember it."
```

This tiered approach keeps the hot cache lean while supporting unlimited scale in deep storage.

## Adding Memory

When the user says "remember this" or you learn something new:

1. **Glossary items** (acronyms, terms, shorthand):
   - Add to `~/.claude/memory/workplace/glossary.md`
   - If frequently used, promote to CLAUDE.md hot cache

2. **People:**
   - Create/update `~/.claude/memory/workplace/people/{name}.md`
   - Add to CLAUDE.md People table if top-30 contact
   - Always capture nicknames — critical for decoding

3. **Projects:**
   - Create/update `~/.claude/memory/workplace/projects/{name}.md`
   - Add to CLAUDE.md Projects table if currently active
   - Capture codenames and alternate references

4. **Company context:** Update `~/.claude/memory/workplace/context/company.md`

## Promotion / Demotion

**Promote to CLAUDE.md hot cache when:**
- A person/term is used frequently across sessions
- It's part of active work

**Demote to deep storage only when:**
- Project completed
- Person no longer a frequent contact
- Term rarely used

This keeps the hot cache fresh. CLAUDE.md should stay under ~40 lines for the Workplace section.

## Recalling Memory

When user asks "who is X" or "what does X mean":

1. Check CLAUDE.md hot cache first
2. Check deep storage for full detail
3. If not found: "I don't know what X means yet. Can you tell me?"

## Conventions

- **Bold** names in hot cache tables for scannability
- Filenames: lowercase, hyphens (`monica-dumitrescu.md`, `key-rotation.md`)
- Always capture nicknames and alternate names
- When something's used frequently, promote it to hot cache
- When something goes stale, demote it to deep storage only
- Keep CLAUDE.md Workplace section under ~40 lines total
