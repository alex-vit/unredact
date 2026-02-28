---
name: go
description: Go conventions, build patterns, and Windows-first gotchas. Covers code style, error handling, goroutines, build tooling, Windows GUI/tray app packaging, Inno Setup, and code generation patterns.
disable-model-invocation: true
---

# Go Patterns & Knowledge

## Constraints

- Avoid CGO. If a dependency requires CGO, ask before using it.
- Don't strive for the latest Go version or features unless there's good reason. If unsure about a newer API or language feature, say so rather than guessing. Check `go.mod` for the actual version in use.

## Code Style

- Prefer `max()`/`min()` builtins over `if` + clamp patterns. E.g. `nearest = max(nearest, 10)` not `if nearest < 10 { nearest = 10 }`.
- Rename functions when names get too similar but do different things. E.g. `autostartEnable`/`autostartEnabled` → `autostartEnable`/`isAutostartEnabled`.

## Error Handling

- Return errors, don't panic. Reserve `panic` for truly unrecoverable programmer errors.
- Never use `Must*()` panic-style helpers in long-running services (servers, daemons, tray apps). A panic crashes the entire process. Always use the error-returning variant and handle the error.
- Thread `context.Context` through API calls and anything that does I/O.

## Goroutines & Functions

- Use range-over-int: `for i := range 3` not `for i := 0; i < 3; i++` (Go 1.22+).
- Extract non-trivial goroutine bodies into named functions: `go autoUpdate()` not `go func() { ... }()`. Keeps the call site readable and the function testable. Place the extracted function in the file that owns its domain (e.g. update logic in `update.go`, not `main.go`).

## Code Maintenance

- Use `go fix ./...` to auto-apply migrations and modernize code (e.g. adopting new stdlib APIs, range-over-int, etc.).
- Use `goimports -w .` to format code, add missing imports, and remove unused ones in one pass. Prefer over `gofmt` — it does everything `gofmt` does plus import management. Run after significant edits.

## Building

```bash
go build ./...                          # build all packages
go test ./...                           # test all packages
go test -run TestName ./path/to/pkg     # single test
go vet ./...                            # static analysis
go test -race ./...                     # catch data races (use when touching concurrency)
goimports -w .                          # format + fix imports
```

ldflags:
```bash
-ldflags "-H=windowsgui"               # Windows: suppress console window for GUI apps
-ldflags "-X main.version=1.2.0"       # inject version at build time
```

These combine: `-ldflags "-X main.version=1.2.0 -H=windowsgui"`.

## Build Tags

```go
//go:build debug    // debug-only code
//go:build !debug   // release-only code
//go:build generate // code generation sources (excluded from normal builds)
//go:build ignore   // excluded entirely (e.g. generators living in another package)
```

Use `const debug = true/false` (not `var`) controlled by build tags for dead-code elimination — the compiler strips unreachable branches.

Build with tags: `go build -tags debug ./...`

## Build Output & Scripts

- Build output goes to `out/` — add `out/` to `.gitignore`, use `-o out/app.exe` in build commands and `OutputDir=out` in Inno Setup.
- Put build/release scripts in `scripts/` (not project root). Standard name: `scripts/build-windows-release.ps1`.

## Cobra + Windows GUI Apps

**Cobra's mousetrap kills GUI apps launched from Explorer.** Cobra includes `inconshreveable/mousetrap` which detects if the parent process is `explorer.exe` (double-click) and exits after showing "This is a command line tool." For CLI tools this is helpful; for GUI apps using cobra it silently kills the app (no console to show the message). Disable it in `init()`:

```go
func init() {
    cobra.MousetrapHelpText = "" // Allow launching from Explorer (GUI app).
}
```

This also affects the registry Run key autostart (explorer.exe processes those entries).

## Windows Paths

- **User config** (`os.UserConfigDir()`): returns `%APPDATA%` — roaming profile, syncs across machines in domain environments. Use for user settings/preferences.
- **Machine-local data** (caches, logs, data with local paths): use `%LocalAppData%` via `os.Getenv("LocalAppData")`. Does not roam.

```go
func localDataDir(appName string) (string, error) {
    dir := os.Getenv("LocalAppData")
    if dir == "" {
        return "", errors.New("cache dir: %LocalAppData% is not set")
    }
    return filepath.Join(dir, appName), nil
}
```

## Windows Tray App Logging

Always log unconditionally to `%LocalAppData%\AppName\log.txt` — don't gate on a debug build tag. A `windowsgui` app has no console anyway, so file logging has no downside. Use `%LocalAppData%` (machine-local), not `%APPDATA%` (roaming) — logs contain local paths and aren't useful across machines.

Use `isoLogWriter` to timestamp each line, and expose the log via a tray menu item:

```go
type isoLogWriter struct{ w io.Writer }

func (lw isoLogWriter) Write(p []byte) (int, error) {
    return fmt.Fprintf(lw.w, "%s %s", time.Now().Format("2006-01-02 15:04:05"), p)
}
```

```go
// in main():
log.SetFlags(0)
dataDir := filepath.Join(os.Getenv("LocalAppData"), "AppName")
os.MkdirAll(dataDir, 0o755)
logPath = filepath.Join(dataDir, "log.txt")
if f, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644); err == nil {
    log.SetOutput(isoLogWriter{f})
}
```

```go
// in tray setup:
systray.AddMenuItem("Open log", "Open log file").Click(func() {
    exec.Command("rundll32", "url.dll,FileProtocolHandler", logPath).Start()
})
```

## Windows Release Packaging (Inno Setup)

### Build script

Put build scripts in `scripts/` (not project root). The standard release script (`scripts/build-windows-release.ps1`) builds the exe to `out/` then runs Inno Setup, producing `out/<app>-setup.exe`. Invoke as:

```powershell
pwsh ./scripts/build-windows-release.ps1 -Version vX.Y.Z
```

The script pattern (see monibright or bot for a full copy):
- Defaults `$Version` to `git describe --tags --always --dirty` if omitted
- Sets `GOOS=windows`, `GOARCH`, `CGO_ENABLED=0`, builds with `-H=windowsgui`
- Finds `iscc.exe` via PATH or `%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe`
- Passes `/DAppVersion=$Version` to ISCC
- Validates both output files exist before returning

### installer.iss conventions

```ini
[Setup]
AppId={{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}  ; generate once, never change
AppMutex=MyAppMutex          ; prevents simultaneous installs
CloseApplications=yes        ; prompt user to close app before overwriting files
PrivilegesRequired=lowest    ; install to {localappdata}, no UAC prompt
DefaultDirName={localappdata}\MyApp
OutputDir=out                ; matches build script output dir
WizardStyle=modern

[Files]
Source: "out\myapp.exe"; DestDir: "{app}"; Flags: ignoreversion

[UninstallDelete]
Type: filesandordirs; Name: "{app}"   ; clean uninstall — no leftover folder
```

Key decisions:
- `CloseApplications=yes` — Inno prompts user to close the running instance (no force-kill needed)
- `UninstallDelete filesandordirs {app}` — removes the entire install folder on uninstall
- `AppId` GUID — Windows uses this to recognise upgrades vs fresh installs; generate once with `[guid]::NewGuid()` in PowerShell and never change it
- `PrivilegesRequired=lowest` + `{localappdata}` — avoids UAC, matches the app's own data directory
- `OutputDir=out` — Inno writes the setup exe to `out/`, consistent with the exe

Autostart registry entry in the ISS must quote the path:
```ini
ValueData: """{app}\myapp.exe"""
```

### Registry autostart in Go code must also quote

```go
func autostartEnable() error {
    exePath, err := os.Executable()
    if err != nil {
        return err
    }
    k, err := registry.OpenKey(registry.CURRENT_USER,
        `Software\Microsoft\Windows\CurrentVersion\Run`, registry.SET_VALUE)
    if err != nil {
        return err
    }
    defer k.Close()
    return k.SetStringValue("MyApp", `"`+exePath+`"`)  // quoted — safe for paths with spaces
}
```

The installer writes a quoted value; code must match. If they diverge (one quoted, one not), toggling autostart from the tray menu loses the quotes silently.

## Running on Windows

- Kill a running process: `powershell -Command "Stop-Process -Name app -Force -ErrorAction SilentlyContinue"`
- Launch detached (non-blocking): `start app.exe`
- Open files/URLs from GUI apps: `rundll32 url.dll,FileProtocolHandler <path>` — do NOT use `cmd /c start`, it silently fails with `-H=windowsgui`.

## .gitignore

Use GitHub's standard Go `.gitignore` as a baseline — it covers binaries (`*.exe`, `*.dll`, `*.so`, `*.dylib`), test artifacts (`*.test`, `*.out`, `coverage.*`), and workspace files (`go.work`). Add project-specific entries (`out/`, `.env`, IDE dirs, `.DS_Store`) as needed.

## Dependencies

Prefer reimplementing thin wrappers over importing large dependencies when only a small fraction of the API surface is used. Evaluate the ratio of used-to-exported symbols before deciding.

## Pattern: go:generate

Use `go:generate` for self-contained code/asset generation with zero external tools. The generated output is committed so builds don't require regeneration.

### Build tag

- `//go:build ignore` — use when the generator is in a different package (e.g. `internal/icon/gen_icon.go` with `package main` inside a `package icon` directory)
- `//go:build generate` — use when the generator is in the same package as the rest of the code (e.g. `gen_languages.go` with `package main` in a `package main` directory)

### Variant A: generate + embed (binary assets)

For binary files (icons, images, data) embedded into the binary at compile time.

```
pkg/
  gen_asset.go    # generator (//go:build ignore, package main)
  asset.go        # //go:generate + //go:embed wrapper
  output.bin      # generated file (committed)
```

```go
// asset.go
//go:generate go run gen_asset.go
package pkg

import _ "embed"

//go:embed output.bin
var Data []byte
```

Real example: monibright `icon/` — `gen_icon.go` generates a multi-size .ico from pure Go (image/png + hand-rolled ICO format).

### Variant B: generate Go source (code generation)

For generating `.go` files — fetching data from APIs, building lookup tables, etc.

```
project/
  gen_thing.go    # generator (//go:build generate, same package)
  thing.go        # generated Go source (committed)
```

Key points:
- Use `go/format` to produce clean, gofmt'd output
- Use `text/template` for the generated file structure
- Add a `// File generated by gen_thing.go; DO NOT EDIT.` header
- The `//go:generate` directive goes in the generator itself

Real example: wt `gen_languages.go` — fetches Wikipedia's language list from the sitematrix API, generates a Go map of supported language codes.
