---
name: go
description: Go conventions, build patterns, ldflags reference, and platform-specific gotchas. Referenced by Go projects for shared patterns — build commands, error handling, build tags, code generation, and Windows-specific concerns.
---

# Go Patterns & Conventions

## Build Commands

```bash
go build ./...                          # build all packages
go test ./...                           # test all packages
go test -run TestName ./path/to/pkg     # single test
go vet ./...                            # static analysis
go generate -tags generate              # code generation (gated by build tag)
```

## ldflags

```bash
-ldflags "-X main.version=1.2.0"       # inject version at build time
-ldflags "-H=windowsgui"               # Windows: suppress console window for GUI apps
```

These combine: `-ldflags "-X main.version=1.2.0 -H=windowsgui"`.

## Build Tags

```go
//go:build debug    // debug-only code
//go:build !debug   // release-only code
//go:build generate // code generation sources (excluded from normal builds)
```

Use `const debug = true/false` controlled by build tags for dead-code elimination — the compiler strips unreachable branches. Use `const`, not `var`.

Build with tags: `go build -tags debug ./...`

## Error Handling

- Return errors, don't panic. Reserve `panic` for truly unrecoverable programmer errors.
- Thread `context.Context` through API calls and anything that does I/O.
- Keep exported API surface minimal.

## Code Generation

Gate generator source files with `//go:build generate` so they're excluded from normal builds. Run with:

```bash
go generate -tags generate
```

## Config Directory

For CLI tools that persist settings, use `os.UserConfigDir()`:

```go
dir, _ := os.UserConfigDir()
configPath := filepath.Join(dir, "appname", "config.json")
```

This gives `%AppData%` on Windows, `~/.config` on Linux, `~/Library/Application Support` on macOS.

## Windows

- **GUI apps**: Use `-H=windowsgui` linker flag to suppress the console window.
- **Opening files/URLs from GUI apps**: Use `rundll32 url.dll,FileProtocolHandler <path>`. Do NOT use `cmd /c start` — it silently fails with `-H=windowsgui`.
- **No CGO preferred**: Prefer pure-Go libraries to avoid CGO cross-compilation complexity on Windows.

## Dependencies

Prefer reimplementing thin wrappers over importing large dependencies when only a small fraction of the API surface is used. Evaluate the ratio of used-to-exported symbols before deciding.
