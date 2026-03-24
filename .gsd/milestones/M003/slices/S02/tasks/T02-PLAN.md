---
estimated_steps: 3
estimated_files: 1
skills_used: []
---

# T02: Remove debug overlay and confirm DEBT-02 already fixed

**Slice:** S02 — Coloring Art Rework
**Milestone:** M003

## Description

Remove the diagnostic debug overlay from `frontend/js/app.js` (DEBT-01). This overlay was a temporary debugging aid for iPad Safari event tracing, activated via `?debug=1` query parameter or triple-tap on the home nav icon. It is no longer needed and should be removed.

Also confirm DEBT-02 (WebKit sparkle E2E test failures) is already fixed by running the sparkle tests explicitly on WebKit. Current state: all 102 tests pass on Chromium, and WebKit sparkle tests have been verified passing in pre-planning exploration.

## Steps

1. **Remove `_initDebug()` function from `frontend/js/app.js`** — Delete the entire debug overlay section: the comment block `// -- Debug overlay -----------------------------------------------------------`, the JSDoc comment, and the `_initDebug()` function body (~60 lines, from line ~310 through ~405 approximately). The function creates a fixed-position diagnostic overlay that logs touch/click/pointer events.

2. **Remove debug activation wiring in DOMContentLoaded** — In the `DOMContentLoaded` event handler at the bottom of `app.js`, remove:
   - The `if (window.location.search.includes("debug=1")) { _initDebug(); }` block (around line 437-439)
   - The triple-tap wiring block: the `const homeNavIcon = ...` variable, `tapCount`, `tapTimer`, and the entire click event listener that calls `_initDebug()` on triple-tap (around lines 442-456)

3. **Run verification** — Confirm no references to `_initDebug` remain. Run full E2E test suite. Run WebKit-specific sparkle tests to confirm DEBT-02 is already resolved.

## Must-Haves

- [ ] `_initDebug` function completely removed from `app.js`
- [ ] `?debug=1` activation code removed from DOMContentLoaded handler
- [ ] Triple-tap wiring (`tapCount`, `tapTimer`, homeNavIcon click listener) removed
- [ ] No remaining references to `_initDebug` anywhere in `app.js`
- [ ] All E2E tests pass on Chromium
- [ ] WebKit sparkle tests pass (confirming DEBT-02 already fixed)
- [ ] Full test suite passes: `uv run pytest -q` shows 102+ passed

## Verification

- `! grep -q "_initDebug" frontend/js/app.js` — no debug overlay references remain
- `! grep -q "debug=1" frontend/js/app.js` — no debug query param check remains
- `! grep -q "tapCount" frontend/js/app.js` — no triple-tap wiring remains
- `uv run pytest tests/test_e2e.py -v` — all E2E tests pass
- `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit` — WebKit sparkle tests pass (DEBT-02 confirmed fixed)
- `uv run pytest -q` — 102+ passed

## Inputs

- `frontend/js/app.js` — contains `_initDebug()` function and its wiring to remove

## Expected Output

- `frontend/js/app.js` — debug overlay code fully removed; DOMContentLoaded handler simplified
