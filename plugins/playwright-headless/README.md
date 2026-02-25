# playwright-headless

Headless Playwright MCP server — background browser automation without a visible window.

Use as a **fallback** for failed `WebFetch` calls (JS-rendered SPAs, 403 bot walls, cookie consent gates) or for background data extraction. For interactive browsing with user login/interaction, use the headed `playwright` plugin instead.

**Limitation**: Does not bypass Cloudflare challenges or advanced bot detection (no stealth patches).

## Install

```
/plugin install playwright-headless@alexv-claude
```
