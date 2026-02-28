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
goimports -w .                          # format code + add missing / remove unused imports
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

## Formatting & Imports

Prefer `goimports -w .` over `gofmt` — it does everything `gofmt` does (formatting) plus automatically adds missing imports and removes unused ones.

## Modernization

Run `go fix ./...` as a final touch before pushing — it applies automatic modernizations for the Go version declared in `go.mod`. It's a bit slow (compiles the full module graph) so don't run it on every save, but do run it after a feature or before a commit batch.

Patterns `go fix` applies automatically, and that you should also use proactively when writing new code:

- `for i := range n` over `for i := 0; i < n; i++` (Go 1.22+)
- `strings.SplitSeq(s, sep)` over `strings.Split(s, sep)` in `range` loops — returns an iterator, avoids allocating the intermediate slice (Go 1.24+)
- `strings.FieldsSeq` / `strings.FieldsFuncSeq` over `strings.Fields` / `strings.FieldsFunc` when iterating (Go 1.24+)
- `maps.Copy(dst, src)` over manual `for k, v := range src { dst[k] = v }` loops (Go 1.21+)
- `slices.Contains(s, v)` over manual linear search loops (Go 1.21+)
- `strings.Cut(s, sep)` over `strings.Index` + manual slice arithmetic (Go 1.18+)
- `any` over `interface{}` (Go 1.18+)
- Remove `omitempty` from `time.Time` struct fields — it was a no-op with the old `encoding/json` behaviour and has surprising semantics in Go 1.26+. Use `omitzero` if you explicitly want zero-value omission.

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

## .gitignore

Use GitHub's standard Go `.gitignore` as a baseline — it covers binaries (`*.exe`, `*.dll`, `*.so`, `*.dylib`), test artifacts (`*.test`, `*.out`, `coverage.*`), and workspace files (`go.work`). Fetch it from `github/gitignore/Go.gitignore` or use `gh repo create --gitignore Go`. Add project-specific entries (`.env`, IDE dirs, `.DS_Store`) as needed.

## Dependencies

Prefer reimplementing thin wrappers over importing large dependencies when only a small fraction of the API surface is used. Evaluate the ratio of used-to-exported symbols before deciding.
