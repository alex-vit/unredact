---
name: cartographer
description: Map codebases by adding structured YAML frontmatter to CLAUDE.md files for instant orientation
user-invocable: true
---

# Cartographer

Map codebases by writing structured orientation data into CLAUDE.md files as YAML frontmatter under a `cartographer:` key. Future sessions load this automatically and skip blind exploration.

## Commands

- **`/cartographer`** — map current directory (shallow: current dir + one level of children)
- **`/cartographer deep`** — recursive mapping using adaptive depth (max depth 4)
- **`/cartographer update`** — refresh all existing cartographer maps in current project
- **`/cartographer status`** — read-only tree of what's mapped, stale (>30 days), unmapped

## CLAUDE.md Frontmatter Schema

All cartographer data lives under a `cartographer:` key in YAML frontmatter. Example:

```yaml
---
cartographer:
  updated: 2026-02-24
  type: monorepo
  summary: Mobile money platform — Django backend, React frontend, shared protobuf schemas
  tech: [python, django, react, protobuf]
  structure:
    backend/: Django API server -> mapped
    frontend/: React SPA -> mapped
    proto/: Protobuf schema definitions
    infra/: Terraform and deployment configs
    scripts/: Developer tooling and CI helpers
  key-files:
    Makefile: Build commands and dev shortcuts
    docker-compose.yml: Local development environment
    .circleci/config.yml: CI pipeline
  patterns:
    - Backend follows Django app-per-domain pattern
    - All API endpoints versioned under /api/v1/
  gotchas:
    - proto/ must be compiled before backend tests will pass
    - frontend/.env.local is not committed — copy from .env.example
---
```

### Field reference

| Field | Required | Description |
|---|---|---|
| `updated` | yes | ISO date (YYYY-MM-DD) of last cartographer update |
| `type` | yes | One of: `monorepo`, `service`, `library`, `app`, `cli`, `module`, `package`, `static-site`, `config`, `workspace` |
| `summary` | yes | One-line description of what this directory/project is |
| `tech` | no | Distinctive technologies (not obvious ones like git) |
| `structure` | no | Significant subdirectories with descriptions. Append `-> mapped` if the subdir has its own cartographer CLAUDE.md |
| `key-files` | no | Important files worth knowing about (max 5-8) |
| `patterns` | no | Architectural patterns and conventions |
| `gotchas` | no | Structural pitfalls and non-obvious requirements |

Omit optional fields when they add no value. Don't list every file — only what helps orientation.

## Body Section

Use a `## Codebase Map` section in the CLAUDE.md body **only** when content needs prose, tables, or more than ~15 structure entries that don't fit neatly in frontmatter.

When used:
- Place it after the project description, before instructional sections (rules, conventions, etc.)
- Include a blockquote attribution line for update tracking: `> Cartographer — updated YYYY-MM-DD`

Most projects need only frontmatter. Don't add a body section by default.

## Merge Strategy

Cartographer edits CLAUDE.md files that may already have content. Rules:

- **Frontmatter**: add or update the `cartographer:` key alongside any existing keys. Never touch other frontmatter keys.
- **Body**: only add or modify a `## Codebase Map` section. Never touch other sections.
- **Existing CLAUDE.md with no frontmatter**: add frontmatter block at the top of the file.
- **No existing CLAUDE.md**: create one with frontmatter only (no body section unless needed).
- **Always preview and confirm** before writing. Show the user what will be added or changed.

## Adaptive Depth

When deciding whether to create a child CLAUDE.md vs. list a subdirectory in the parent's `structure:`:

**Go deeper** (create a child CLAUDE.md) when the directory:
- Already has its own CLAUDE.md
- Has its own build system (package.json, Cargo.toml, go.mod, setup.py, etc.)
- Is a top-level child of a monorepo
- Has >10 source files and >3 subdirectories

**Stay shallow** (list in parent's `structure:`) when the directory:
- Has <5 files and no subdirectories
- Is generated, vendored, or hidden (node_modules, .git, dist, vendor, etc.)
- Would exceed depth 4 from the project root

When going deeper, mark the entry in the parent's `structure:` with `-> mapped`.

## Mapping Process

1. **Survey** — list the directory contents, read existing CLAUDE.md (if any), check for build files and project markers.
2. **Classify** — determine `type`, identify key technologies, note structural patterns.
3. **Draft frontmatter** — assemble the `cartographer:` block with only the fields that add value.
4. **Check children** (if deep mapping) — apply adaptive depth rules to decide which subdirectories get their own maps.
5. **Preview** — show the user what will be written and where.
6. **Write** — after confirmation, write the CLAUDE.md file(s).

For `/cartographer update`: re-survey each mapped directory, diff against existing data, and only update what's changed. Show a summary of changes before writing.

For `/cartographer status`: walk the project tree, find all CLAUDE.md files with `cartographer:` frontmatter, and display:
- Mapped directories with their `updated` dates
- Stale maps (>30 days since update) — marked as stale
- Unmapped directories that meet the "go deeper" criteria — marked as candidates

## Auto-triggers

Suggest mapping (never map silently) when:
- The user asks structural questions: "what does this project do", "how is this organized", "what's in this directory"
- About to explore a directory that has no cartographer data — suggest mapping first
- A map is stale (>30 days) — mention once per session: "Cartographer map is from [date] — `/cartographer update` to refresh"

**Do NOT trigger** during:
- Focused implementation work
- Quick fixes or single-file changes
- If the user has declined mapping this session

## Interactions

- **Notes**: complementary. Cartographer maps structure; notes track decisions and progress on tasks. No overlap.
- **Save-state**: complementary. Cartographer is durable (persists across sessions); save-state is ephemeral (session position snapshots).
- **Reflect**: distinct. Cartographer captures structural facts; reflect captures behavioral rules. Cartographer data goes in project CLAUDE.md; reflect rules go in `~/.claude/CLAUDE.md`.
- **Squire**: no interaction.

## Tone

Utilitarian. Terse descriptions, structured data. Match the existing style of whatever CLAUDE.md file is being edited. No prose where a key-value pair will do.
