---
title: Skill Ideas
created: 2026-02-22
updated: 2026-02-24
tags: [plugins, skills]
status: active
sections:
  - Bisect — automated git bisect skill, highest-value remaining idea
---

# Skill Ideas

## `/bisect` (automated git bisect)
- **Source:** [Superpowers](https://github.com/obra/superpowers)
- Describe the bug, skill writes a test/check, runs `git bisect` autonomously, reports offending commit
- Leverages Bash + sub-agents
- Showcases autonomous agent capability, huge time saver

## Decisions

- Full scouting report saved to `~/Sync/claude/2026-02-22-skill-ideas-scouting.md`
- All other ideas removed — meta-prompting, compound, research, explain, changelog, scaffold, deps, pr-prep, issue, timebox, audit-skills
- `/save-state` built and removed — overlapped with notes
- `/context`, `/review` removed — not pursuing
- `/reflect` removed — writing CLAUDE.md rules manually is sufficient
- `/notes` + `/squire` merged into `/productivity`
- "3+ failures" escalation moved to CLAUDE.md as a behavioral rule
