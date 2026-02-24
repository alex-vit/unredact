---
name: bisect
description: Find the commit that broke something. Use when the user wants to find which commit introduced a regression, when something "used to work", or when bisecting git history to isolate a bug.
argument-hint: "[test-command]"
---

# Git Bisect

Find the commit that introduced a regression using binary search through git history.

## Usage

- `/bisect` — interactive setup, manual testing mode
- `/bisect <test-command>` — automated mode using `git bisect run`
- `/bisect stop` — abort an in-progress bisect session

## Argument parsing

- If the argument is `stop`, go to **Abort** below.
- If there is no argument, proceed with interactive setup in **manual** mode.
- Otherwise, treat the entire argument string as the test command for **automated** mode.

## Abort (`/bisect stop`)

Check if a bisect session is active:

```bash
git bisect log 2>/dev/null
```

If active, reset it:

```bash
git bisect reset
```

Then report the result ("Bisect session aborted." or "No bisect session in progress."). Done — stop here.

## Preflight checks

Run these checks before any setup:

### 1. Verify git repo

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
```

If not a git repo, tell the user and stop.

### 2. Detect existing bisect session

```bash
git bisect log 2>/dev/null
```

If a session exists, use `AskUserQuestion` to ask the user:
- **Continue** — resume the existing session (skip setup, go straight to the execution loop)
- **Reset and start fresh** — run `git bisect reset` then proceed with setup

### 3. Detect dirty working tree

```bash
git status --porcelain
```

If there are uncommitted changes, use `AskUserQuestion` to ask:
- **Stash changes** — run `git stash push -m "bisect: auto-stash"` and remember to pop later
- **Continue anyway** — proceed without stashing (warn that checkout will fail if files conflict)
- **Cancel** — stop the bisect

## Setup

### Bad commit

Use `AskUserQuestion` to ask for the bad commit. Default is HEAD. Accept any commit-ish (SHA, tag, branch name, HEAD~N).

### Good commit

Use `AskUserQuestion` to ask for the last known good commit. This is required — there is no default.

If the user doesn't know, help them find one:
- Show recent tags: `git tag --sort=-version:refname | head -10`
- Show recent history: `git log --oneline -20`
- Let them pick from the list

### Start bisect

```bash
git bisect start
git bisect bad <bad-commit>
git bisect good <good-commit>
```

After these commands, git will check out the first commit to test and report how many revisions are left (roughly log2 of the range).

## Automated mode

When the user provided a test command:

```bash
git bisect run <test-command>
```

The test command must exit 0 for good commits and non-zero (1-124, 126, 127) for bad commits. Exit code 125 means "skip this commit" (can't test).

After `git bisect run` completes, go to **Results**.

## Manual mode

Loop until git finds the culprit:

1. Show the current commit being tested:

```bash
git log --oneline -1
```

Also show how many steps remain:

```bash
git bisect log 2>/dev/null | head -1
```

2. Use `AskUserQuestion` to ask the user to test this commit:
   - **Good** — this commit does NOT have the bug
   - **Bad** — this commit HAS the bug
   - **Skip** — can't test this commit (build failure, etc.)

3. Run the corresponding command:

```bash
git bisect good   # or bad, or skip
```

4. Check if git has found the culprit — the output will contain the first bad commit info. If not found yet, repeat from step 1.

## Results

When bisect completes, it identifies the first bad commit. Display it clearly:

```bash
git show --stat <culprit-sha>
```

Summarize:
- The culprit commit (SHA, author, date, message)
- What files were changed
- The total number of commits that were tested

## Cleanup

After presenting results (or on any error/abort):

1. Reset the bisect session:

```bash
git bisect reset
```

2. If changes were stashed during preflight, pop them:

```bash
git stash pop
```
