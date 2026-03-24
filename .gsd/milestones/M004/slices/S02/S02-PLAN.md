# S02: Icon Refresh

**Goal:** All nav bar and home screen icons are semantically meaningful — mermaid tail for dress-up, palette/pencil for coloring, house for home.
**Demo:** Open the app, see a house icon (home), mermaid tail icon (dress-up), and pencil icon (coloring) in the nav bar. Home screen activity buttons show matching mermaid tail and pencil icons in circles.

## Must-Haves

- Nav bar dress-up icon is a bifurcated mermaid tail (not a star)
- Home screen dress-up activity button icon is a mermaid tail (not a star)
- Coloring pencil and home house icons remain unchanged
- No CSS, routing, or JS behavior changes — SVG path data only
- E2E tests assert icon semantic attributes (aria-labels distinct, SVG children present)
- ICON-01 requirement marked validated

## Observability / Diagnostics

**Runtime signals:**
- Nav icon SVG paths are inline in `frontend/index.html` — open DevTools Elements panel, expand `<nav id="nav-bar">`, inspect `<a href="#/dressup">` SVG children to confirm mermaid tail paths are present.
- Home screen button SVG is rendered by `renderHome()` in `frontend/js/app.js` — open the app at `#/home`, right-click the dress-up button → Inspect to see the rendered SVG content.

**Inspection surface:**
- `grep -n "path d=" frontend/index.html` — lists all SVG path data in nav; should show no star polygon coordinates.
- `grep -n "path d=" frontend/js/app.js` — lists all SVG path data in app.js renderHome(); should show no star polygon coordinates.
- Browser console: no SVG parse errors on load. Any malformed `d=` attribute produces a silent render failure (icon disappears), visible in DevTools.

**Failure visibility:**
- If a path `d` attribute is malformed, the SVG element renders blank — the icon area shows only the circle background (for home screen) or empty space (for nav).
- To confirm correct rendering visually: `cd frontend && python3 -m http.server 8080 > /dev/null 2>&1 &` then open `http://localhost:8080/index.html` in a browser.

**Redaction:** No secrets or PII involved. All data is static SVG path geometry.

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q` — all E2E tests pass including new icon semantic tests
- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/ -x -q` — full suite stays at 111+ tests passing
- `grep -q "star" frontend/index.html` exits 1 (no star path remains in nav)
- `grep -c "TestIconSemantics" tests/test_e2e.py` returns 1
- `grep -q "M16 2L18 10L26 10" frontend/index.html` exits 1 (old star path absent from nav)
- `grep -q "M40 12L44 28L56 28" frontend/js/app.js` exits 1 (old star path absent from home button)

## Tasks

- [x] **T01: Replace dress-up star icons with mermaid tail SVG paths** `est:20m`
  - Why: The dress-up star icon is meaningless for "dress up your mermaid." A bifurcated mermaid tail is the semantic icon. This is the core deliverable of the slice.
  - Files: `frontend/index.html`, `frontend/js/app.js`
  - Do: Replace the 5-pointed star `<path>` in `index.html` line 24 with a bifurcated mermaid tail (2-3 paths, 32×32 viewBox, same `#c47ed0`/`#f0d4f5` colors). Replace the star `<path>` in `app.js` `renderHome()` with a tail icon scaled to 80×80 viewBox (keep circle background, remove old star path, replace with tail). Keep the existing tail-curve line `M28 58Q...` or replace with the unified tail design.
  - Verify: `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q` — existing tests still pass (no regressions)
  - Done when: Both star paths replaced with mermaid tail paths, existing E2E tests pass, no CSS/JS logic changes

- [x] **T02: Add icon semantic E2E tests and validate ICON-01** `est:15m`
  - Why: Proves the icon refresh delivers on ICON-01 — icons are present, distinct, and semantically labeled. Without tests, the requirement has no automated validation.
  - Files: `tests/test_e2e.py`
  - Do: Add `class TestIconSemantics` with tests: (1) each `.nav-icon` has non-empty `aria-label`, (2) nav icon aria-labels are all distinct, (3) each `.nav-icon` contains an `<svg>` child, (4) each `.activity-btn` contains an `<svg>` child and has a non-empty `aria-label`. Use the existing `app_page` fixture pattern.
  - Verify: `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py::TestIconSemantics -x -v` — all new tests pass
  - Done when: TestIconSemantics class exists with 3+ passing tests, full suite at 111+ tests, ICON-01 validation field updated

## Files Likely Touched

- `frontend/index.html`
- `frontend/js/app.js`
- `tests/test_e2e.py`
