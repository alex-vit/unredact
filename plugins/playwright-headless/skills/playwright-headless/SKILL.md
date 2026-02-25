---
name: playwright-headless
description: Headless browser automation — use as a fallback for failed WebFetch calls or background tasks that don't need a visible window. Not the default; prefer the headed `playwright` plugin for interactive use.
---

# Headless Playwright Browser

Headless Playwright — no visible window. Use this as a **fallback**, not the default.

## When to use

Use headless Playwright when:

- **WebFetch fails** and a real browser would help — JS-rendered SPAs, 403 bot walls, cookie consent gates, lazy-loaded content, GDPR walls.
- **Background data extraction** — scraping, screenshots, network inspection where no user interaction is needed.
- **No user input required** — if the user doesn't need to see or interact with the page, headless is lighter.

**Do NOT use for:**
- Anything requiring user login, MFA, or manual interaction — use the headed `playwright` plugin instead.
- When the user asks to "open" a site — they want a visible window.

## Tool discovery

Find tools with `ToolSearch` query `"playwright-headless"`. All tools are prefixed `mcp__plugin_playwright-headless_playwright__browser_*`.

## Core workflow

1. **Navigate** — `browser_navigate` to the URL
2. **Snapshot** — `browser_snapshot` to get an accessibility-tree view of the page (text + interactive refs)
3. **Interact** — `browser_click`, `browser_fill_form`, `browser_select_option`, `browser_press_key` using `ref` values from the snapshot
4. **Extract** — `browser_evaluate` to run JS and pull data, or `browser_take_screenshot` for visuals
5. **Close** — `browser_close` when done

## Recipes

### Screenshot
```
navigate → take_screenshot
```

### Read a JS-rendered SPA
```
navigate → snapshot → (extract text from snapshot)
```

### Dismiss cookie consent wall
```
navigate → snapshot → click the "Accept" / "Agree" ref → snapshot again
```

### Inspect CSS / fonts
```
navigate → evaluate: "JSON.stringify(window.getComputedStyle(document.querySelector('selector')))"
```
For fonts specifically:
```
evaluate: "window.getComputedStyle(document.querySelector('body')).fontFamily"
```

### Inspect network requests
```
navigate → network_requests
```

### Inspect console errors
```
navigate → (interact) → console_messages
```

### Run arbitrary JS
```
evaluate: "document.title"
evaluate: "document.querySelectorAll('a').length"
evaluate: "[...document.querySelectorAll('h1,h2,h3')].map(e => e.textContent)"
```

## Gotchas

- **Snapshot vs screenshot**: `browser_snapshot` returns an accessibility tree (text, refs for interaction). `browser_take_screenshot` returns an image. Use snapshot for data extraction, screenshot for visuals.
- **Refs are required for interaction**: You must `browser_snapshot` first to get `ref` values, then pass them to `browser_click` etc. You cannot click by CSS selector.
- **`browser_evaluate` takes a JS expression string**, not a function. Return the value directly.
- **Always `browser_close`** when you're done to free resources.
- **One browser at a time**: The MCP server manages a single browser instance. Close before opening a new context.
- **Cloudflare / advanced bot detection**: Headless Chromium gets fingerprinted by Cloudflare, Akamai, etc. Sites like Medium that use JS challenges will show "Just a moment..." indefinitely. No stealth plugins are loaded.
