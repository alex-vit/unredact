# Skill Ideas — Shortlisted

Status: Research — In Progress

## Goals

Evaluate and potentially build new skills/hooks for the plugin collection, sourced from community scouting (r/ClaudeCode, awesome-claude-code, Trail of Bits, Compound Engineering, Superpowers, TÂCHES, claudekit).

## Shortlisted Ideas

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

## Decisions

- Full scouting report saved to `~/Sync/claude/2026-02-22-skill-ideas-scouting.md`

## TODOs

- [ ] Decide which ideas to build first
- [ ] Prototype shortlisted items
- [ ] Evaluate whether "3+ failures" is better as a CLAUDE.md rule or a skill
