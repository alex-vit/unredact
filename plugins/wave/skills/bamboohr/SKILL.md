---
name: bamboohr
description: Interact with BambooHR (wavemm.bamboohr.com) — time off requests and other HR tasks via headed Playwright
user-invocable: true
---

# BambooHR

Interact with BambooHR (wavemm.bamboohr.com) using the headed Playwright browser.

## Prerequisites

- The `playwright` plugin must be installed (provides `mcp__plugin_playwright_playwright__*` tools).
- The user must log in manually after the browser opens (Google SSO or email/password). Wait for login before proceeding.

## Getting started

1. **Navigate** to `https://wavemm.bamboohr.com`.
2. **Wait for login** — the user will authenticate. You'll know login succeeded when the page URL is `/home/` and you can see the user's name in the snapshot.
3. Proceed with the requested task.

## Time off requests

### Workflow

1. From the home page, **click "Request Time Off"**.
2. **Fill the form:**
   - **From / To** — dates in `dd/mm/yyyy` format. Type into the textboxes, then Tab out to commit.
   - **Time Off Category** — click the dropdown, then select from the menu. Default to "Annual Vacation Leave" unless the user specifies otherwise.
   - **Amount** — auto-populated after dates + category are set. Confirm with the user.
   - **Note** — leave blank unless the user provides one.
3. **Confirm before submitting** — always tell the user the summary (dates, category, total days) and ask for confirmation before clicking "Send Request".
4. **Submit** — click "Send Request". Success redirects to the Time Off page.

### Date interpretation

- "Tomorrow" = today + 1 day.
- "Friday" = the upcoming Friday (or today if today is Friday).
- "Next week" = Monday–Friday of the following week.
- When the user gives two separate days (e.g. "tomorrow and Friday"), use the earliest as From and latest as To. If there are gaps (non-contiguous days), warn the user that BambooHR will count all days in the range and ask if that's what they want.

### Multiple requests

If the user needs non-contiguous days off (e.g. Monday and Friday but not Tue–Thu), submit separate requests for each block.

### Categories

Common categories and when to use them:
- **Annual Vacation Leave** — default for any personal time off
- **Sick Leave** — illness
- **Statutory Holiday (Remote)** — local public holidays for remote workers
- **Parental Leave** — parental leave
- **Bereavement Leave** — bereavement

Don't guess — if the reason is ambiguous, ask.

## Gotchas

- Chrome must not already be running when launching headed Playwright. If launch fails with "Opening in existing browser session", ask the user to close Chrome first.
- The date fields use `dd/mm/yyyy` format, not US format.
- After filling each date, press Tab to commit the value before moving to the next field.
- The "Amount" field is disabled — it auto-calculates from dates + category. Don't try to fill it.
