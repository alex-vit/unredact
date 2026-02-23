# Skill Ideas — Shortlisted

Status: Research — In Progress

## Goals

Evaluate and potentially build new skills/hooks for the plugin collection, sourced from community scouting (r/ClaudeCode, awesome-claude-code, Trail of Bits, Compound Engineering, Superpowers, TÂCHES, claudekit) and brainstorming.

## Shortlisted Ideas (from scouting)

### Meta-prompting (create-prompt + run-prompt)
- **Source:** [TÂCHES](https://github.com/glittercowboy/taches-cc-resources)
- `/create-prompt` generates a rigorous prompt from conversation context
- `/run-prompt` executes it in a fresh sub-agent context (clean slate)
- Key insight: separates analysis (full context) from execution (clean context), prevents context pollution in long sessions

### Structured problem/solution KB (`/compound`)
- **Source:** [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin)
- Captures problem-solution pairs in structured markdown with YAML frontmatter
- Stored in `docs/solutions/[category]/`, Grep-searchable via frontmatter fields
- Auto-invokes on "that worked", "it's fixed"
- Escalation: individual fix → common pattern (3+) → Required Reading
- Complements `/reflect` — reflect = terse rules, compound = full investigation trail

### "3+ failures = question architecture" escalation
- **Source:** [Superpowers](https://github.com/obra/superpowers)
- If three fix attempts fail, stop patching and question the approach itself
- Prevents infinite "one more fix" loops
- Could go directly in CLAUDE.md as a behavioral rule rather than a full skill

### Research skill (`/research`)
- **Source:** [last30days-skill](https://github.com/mvanhorn/last30days-skill)
- Research any topic across Reddit, X, YouTube, web
- Synthesize findings with engagement metrics and source attribution
- Save output to dated artifact files with machine-readable metadata
- Reusable for future context

## New Ideas (brainstormed)

### Context & Memory

#### `/save-state` (checkpoint + handoff)
- Snapshot current session state: what we're doing, key decisions, open questions, what's unfinished
- Generates a structured briefing a future session can pick up from
- Composable with squire (auto-save on session wind-down) and notes (links to relevant note files)
- **Status: Done** — see `plugins/save-state/`

#### `/context` (project bootstrap)
- Auto-generate a focused CLAUDE.md section for the current project by scanning the repo
- Detects build system, test runner, linter config, directory conventions, dependencies
- Bootstraps a new project's CLAUDE.md in seconds instead of manual authoring

#### `/stash` (conversation context stack)
- Like git stash but for conversation context — park current work, switch to something urgent, pop to resume
- Builds on save-state but adds stack semantics (push/pop)

### Code Quality & Review

#### `/review` (pre-commit review)
- Review staged/unstaged changes against project conventions (from CLAUDE.md), common pitfalls, security checklist
- Lightweight pre-commit review
- Could feed into reflect if it finds recurring issues

#### `/explain` (deep-dive code explanation)
- Deep-dive explanation of a file, function, or module with call graph, side effects, "why it's weird" annotations
- Outputs to temp file or inline; useful for onboarding onto unfamiliar code

#### `/changelog`
- Generate human-readable changelog entry from recent commits (since last tag or N commits)
- Follows Keep a Changelog format
- Pulls context from dev notes for richer entries

### Workflow Automation

#### `/bisect` (automated git bisect)
- Describe the bug, skill writes a test/check, runs `git bisect` autonomously, reports offending commit
- Leverages Bash + sub-agents

#### `/scaffold` (convention-aware boilerplate)
- Detects patterns in existing code ("all handlers follow this shape") and generates new files matching them
- Convention-aware, not template-based

#### `/deps` (dependency health)
- Analyze outdated packages, known CVEs, unused deps, license issues
- Runs the right tool per ecosystem (npm audit, go mod tidy, pip-audit)
- Outputs actionable summary

### Communication & Collaboration

#### `/pr-prep` (PR preparation)
- Generates description from commits + notes, suggests reviewers via git blame
- Creates self-review checklist, flags files that commonly cause review friction

#### `/issue` (conversation → GitHub issue)
- Turn a conversation into a well-structured GitHub issue
- Extracts repro steps, expected vs actual, relevant code references
- Composable with squire (creates linked todo)

### Meta / Developer Experience

#### `/timebox` (scope limiter)
- Set a scope limit ("spend max 15 minutes on this")
- Tracks tool calls, warns when approaching limit, suggests what to hand off vs. finish
- Prevents rabbit holes — the #1 complaint with AI-assisted workflows

#### `/audit-skills` (skill ecosystem introspection)
- Introspect installed skills: overlapping triggers, redundancies, gaps
- Useful as skill count grows — keeps the system composable without hidden conflicts

## Highest-Value Picks

| Skill | Why |
|---|---|
| `/save-state` | Universal session management — every user needs this |
| `/context` | Instant project onboarding — massive time saver |
| `/review` | Natural pre-commit workflow, feeds into reflect |
| `/bisect` | Showcases autonomous agent capability, huge time saver |
| `/timebox` | Unique to AI-assisted workflows, prevents rabbit holes |

## Decisions

- Full scouting report saved to `~/Sync/claude/2026-02-22-skill-ideas-scouting.md`
- `/save-state` chosen as first new skill to build (combines checkpoint + handoff)

## TODOs

- [x] Decide which ideas to build first → `/save-state`
- [x] Prototype `/save-state`
- [ ] Evaluate whether "3+ failures" is better as a CLAUDE.md rule or a skill
- [ ] Prototype remaining shortlisted items
