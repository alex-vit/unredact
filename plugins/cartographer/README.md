# cartographer

Codebase mapping — leaves structured breadcrumbs in CLAUDE.md files for instant orientation.

Every new session in an unfamiliar codebase starts with expensive exploration: listing directories, reading files, building a mental model from scratch. Cartographer solves this by writing structured YAML frontmatter into CLAUDE.md files, creating a navigable map that future sessions load automatically.

Maps are shallow by default (current directory + one level of children) and go deeper adaptively for monorepos and complex projects.

## Install

```
/plugin install cartographer@alexv-claude
```
