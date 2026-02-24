# playwright-headless

Headless Playwright MCP server with behavioral guidance for when to use browser automation instead of `WebFetch`.

Provides the `playwright-mcp --headless` MCP server plus a reference skill that teaches Claude Code when to reach for Playwright tools — simple 403 bot walls, JS-rendered SPAs, cookie consent gates, CSS/font inspection, screenshots, and more.

**Limitation**: Does not bypass Cloudflare challenges or advanced bot detection (no stealth patches). Sites like Medium will block headless Chromium the same as `WebFetch`.

## Install

```
/plugin install playwright-headless@alexv-claude
```
