---
id: T01
parent: S03
milestone: M003
provides:
  - resp.ok guards on all three frontend fetch calls prevent silent HTML-body corruption when assets return HTTP errors
key_files:
  - frontend/js/app.js
  - frontend/js/dressup.js
key_decisions:
  - Threw inside existing try/catch blocks rather than adding new ones, keeping error-handling surface minimal
patterns_established:
  - After every fetch(), immediately check resp.ok and throw a descriptive Error before calling resp.text()
observability_surfaces:
  - Error message surface: browser console + the existing error div ("Could not load mermaid." / "Could not load coloring page.") now shows on any HTTP error status instead of silently rendering garbage SVG
duration: ~5min
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T01: Add resp.ok checks to all fetch calls in app.js and dressup.js

**Added `resp.ok` guards to all three frontend fetch() calls so HTTP error responses throw instead of silently injecting HTML into SVG rendering paths.**

## What Happened

Three `fetch()` calls in `renderDressUp()` (app.js), `renderColoringPage()` (app.js), and `fetchCharacterSVG()` (dressup.js) were reading the response body unconditionally regardless of HTTP status. A 404 or 500 would return HTML, which then got injected as SVG content, corrupting the UI silently.

Applied three surgical one-liner additions immediately after each fetch call:

1. `frontend/js/app.js` — after `fetch("assets/svg/mermaid.svg")` in `renderDressUp()`:
   `if (!resp.ok) throw new Error(\`Failed to load mermaid SVG: ${resp.status}\`);`

2. `frontend/js/app.js` — after `fetch(page.file)` in `renderColoringPage()`:
   `if (!svgResp.ok) throw new Error(\`Failed to load coloring page: ${svgResp.status}\`);`

3. `frontend/js/dressup.js` — after `fetch(\`assets/svg/dressup/${characterId}.svg\`)` in `fetchCharacterSVG()`:
   `if (!resp.ok) throw new Error(\`Failed to load character SVG: ${resp.status}\`);`

Both app.js throws land inside existing try/catch blocks (lines 56–108 and 152–304) that render the error div. The dressup.js throw propagates to the app.js caller which is also inside a try/catch — no new error handling needed.

No `?v=14` cache busters were touched.

## Verification

- `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` → 2 ✅
- `grep -c "resp.ok" frontend/js/dressup.js` → 1 ✅
- `uv run pytest -q` → 103 passed, 0 failed ✅
- `grep -c "?v=14" frontend/js/app.js frontend/js/dressup.js` → 3 + 1 (unchanged) ✅

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `grep -c "resp\.ok\|svgResp\.ok" frontend/js/app.js` | 0 (output: 2) | ✅ pass | <1s |
| 2 | `grep -c "resp\.ok" frontend/js/dressup.js` | 0 (output: 1) | ✅ pass | <1s |
| 3 | `uv run pytest -q` | 0 | ✅ pass | 46.9s |
| 4 | `grep -c "?v=14" frontend/js/app.js frontend/js/dressup.js` | 0 (3+1) | ✅ pass | <1s |

## Diagnostics

- **Failure signal:** If any of the three asset fetches fail at runtime, the browser console will show a thrown Error with the HTTP status (e.g., `Failed to load mermaid SVG: 404`). The UI will display the existing error div rather than silently rendering broken SVG.
- **Inspection command:** `grep -n "resp.ok\|svgResp.ok" frontend/js/app.js frontend/js/dressup.js` shows all three guard locations.

## Deviations

None — implementation matched the plan exactly.

## Known Issues

None.

## Files Created/Modified

- `frontend/js/app.js` — added two `resp.ok` / `svgResp.ok` checks after fetch calls in `renderDressUp()` and `renderColoringPage()`
- `frontend/js/dressup.js` — added one `resp.ok` check after fetch call in `fetchCharacterSVG()`
