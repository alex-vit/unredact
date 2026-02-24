---
name: playwright-headless
description: Headless browser automation — use instead of WebFetch for JS-rendered pages, SPAs, screenshots, CSS/font inspection, simple 403s, cookie consent walls, GDPR gates, lazy-loaded content, form interaction, network inspection, and any page that returns empty or garbled content from WebFetch. Does not bypass Cloudflare or advanced bot detection.
---

# Headless Playwright Browser

## When to use instead of WebFetch

Reach for Playwright when:

- **403 / bot detection** — sites that return 403 to `WebFetch` due to missing browser headers. Note: sites behind **Cloudflare challenges** (e.g. Medium) will block headless Playwright too — no stealth patches are installed.
- **JS-rendered SPAs** — WebFetch gets empty `<div id="root"></div>` shells.
- **Cookie consent / GDPR / age gates** — requires clicking "Accept" before content is visible.
- **Dynamic or lazy-loaded content** — infinite scroll, "Load more" buttons, content behind tabs.
- **Screenshots** — visual proof, UI verification, sharing what a page looks like.
- **CSS / font / layout inspection** — computed styles, font families, colors, spacing via `evaluate`.
- **Form interaction / multi-step flows** — login, search, pagination, wizard forms.
- **WebFetch returns empty or garbled content** — retry the same URL with Playwright.
- **Network traffic / console error inspection** — debug what a page loads or logs.

If WebFetch works fine, keep using it. Playwright is heavier — use it when you need it.

## Tool discovery

Find tools with `ToolSearch` query `"playwright"`. All tools are prefixed `mcp__plugin_playwright-headless_playwright__browser_*`.

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
