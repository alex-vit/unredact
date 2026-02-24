# bisect

Interactive git bisect workflow — find the commit that introduced a regression.

- **Automated mode**: provide a test command and let `git bisect run` do the work
- **Manual mode**: Claude asks you to test each commit and interprets your response

Handles dirty working trees (stash), existing bisect sessions (continue/reset), and cleanup.

## Install

```
/plugin install bisect@alexv-claude
```

## Usage

```
/bisect                          # interactive setup — manual mode
/bisect "make test"              # automated mode with test command
/bisect stop                     # abort an in-progress bisect
```
