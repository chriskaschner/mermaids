---
estimated_steps: 3
estimated_files: 2
skills_used:
  - best-practices
---

# T01: Add resp.ok checks to all fetch calls in app.js and dressup.js

**Slice:** S03 — Cleanup & Stability
**Milestone:** M003

## Description

Three `fetch()` calls in the frontend JS silently accept HTTP error responses (404, 500, etc.) and pass the HTML error page body into code that expects SVG content. This corrupts the UI — the user sees raw HTML where an SVG should render. The fix is simple: check `resp.ok` after each fetch and throw if false. The existing try/catch blocks will catch the error and render the error div that's already coded.

**Important constraints:**
- Do NOT change the `?v=14` cache buster query strings in any import statements.
- Do NOT add new try/catch blocks — use the existing ones at lines 56/108 and 152/304 in app.js.
- The dressup.js `fetchCharacterSVG()` has no try/catch — the throw will propagate to callers. This is acceptable as the callers are within try/catch in app.js.

## Steps

1. In `frontend/js/app.js` line 57 (`const resp = await fetch("assets/svg/mermaid.svg")`), add after the fetch line:
   ```javascript
   if (!resp.ok) throw new Error(`Failed to load mermaid SVG: ${resp.status}`);
   ```
   This is inside the try block starting at line 56, caught at line 108.

2. In `frontend/js/app.js` line 223 (`const svgResp = await fetch(page.file)`), add after the fetch line:
   ```javascript
   if (!svgResp.ok) throw new Error(`Failed to load coloring page: ${svgResp.status}`);
   ```
   This is inside the try block starting at line 152, caught at line 304.

3. In `frontend/js/dressup.js` line 51 (`const resp = await fetch(...)`), add after the fetch line:
   ```javascript
   if (!resp.ok) throw new Error(`Failed to load character SVG: ${resp.status}`);
   ```

## Must-Haves

- [ ] `resp.ok` check added after the mermaid.svg fetch in `renderDressUp()` (app.js)
- [ ] `svgResp.ok` check added after the coloring page SVG fetch in `renderColoringPage()` (app.js)
- [ ] `resp.ok` check added after the character SVG fetch in `fetchCharacterSVG()` (dressup.js)
- [ ] No `?v=14` cache busters changed
- [ ] Full test suite still passes at 103+

## Verification

- `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` → 2
- `grep -c "resp.ok" frontend/js/dressup.js` → 1
- `uv run pytest -q` → 103+ passed, 0 failed

## Observability Impact

- Signals added/changed: Fetch failures now throw descriptive `Error` messages (e.g. `Failed to load mermaid SVG: 404`) instead of silently passing HTML error pages to SVG rendering code. These errors are caught by existing try/catch blocks which render error divs visible to the user.
- How a future agent inspects this: `grep -n "resp.ok" frontend/js/app.js frontend/js/dressup.js` — confirms all 3 guards are present. In the browser, a 404 on any SVG fetch will show an error div instead of a broken layout.
- Failure state exposed: HTTP error status codes now surface as thrown errors with the status code in the message, caught by existing error UI. Previously, failures were invisible — the HTML error page was silently injected as SVG content.

## Inputs

- `frontend/js/app.js` — contains two fetch calls needing resp.ok checks (lines 57 and 223)
- `frontend/js/dressup.js` — contains one fetch call needing resp.ok check (line 51)

## Expected Output

- `frontend/js/app.js` — modified with two resp.ok checks added
- `frontend/js/dressup.js` — modified with one resp.ok check added
