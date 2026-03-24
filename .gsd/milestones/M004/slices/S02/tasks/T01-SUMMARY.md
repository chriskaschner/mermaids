---
id: T01
parent: S02
milestone: M004
provides:
  - mermaid tail SVG icon replacing star in nav bar dress-up link
  - mermaid tail SVG icon replacing star in home screen dress-up activity button
key_files:
  - frontend/index.html
  - frontend/js/app.js
key_decisions:
  - Mermaid tail design uses cubic-bezier curves (C commands) for a narrow stem + bifurcated-lobes silhouette; deliberately not a flat fish-tail to read clearly at 32×32
  - Unified stem-midline accent path retained in 80×80 version to reinforce the tail concept inside the circle
patterns_established:
  - Inline SVG icon replacement: keep the `<svg>` wrapper attributes unchanged, replace only the `<path d="...">` child elements
observability_surfaces:
  - grep "path d=" frontend/index.html — confirms C-curve mermaid tail in dress-up nav icon
  - grep "path d=" frontend/js/app.js — confirms C-curve mermaid tail in renderHome() dress-up button
  - DevTools Elements panel > nav-bar > dressup anchor > svg > path.d attribute
duration: ~5m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T01: Replace dress-up star icons with mermaid tail SVG paths

**Replaced both dress-up star polygon paths with bifurcated mermaid tail cubic-bezier paths in index.html (32×32 nav) and app.js renderHome() (80×80 button); all 14 E2E tests pass with no regressions.**

## What Happened

Read `frontend/index.html` and `frontend/js/app.js` to confirm the exact star path strings, then designed a bifurcated mermaid tail using cubic-bezier curves: a narrow stem descending from the top-center, splitting into two curved lobes at roughly 60% down, giving a clear Y-fork / fish-tail silhouette. The 32×32 nav version uses two paths (tail body + stem midline accent). The 80×80 home button version scales the same design up, retaining the circle background; the old wavy-line accent was replaced by a clean stem accent path.

Both replacements are SVG path data only — no CSS classes, JS logic, routing, or event handlers were touched. The house and pencil icons were verified unchanged.

Pre-flight observability gaps were also fixed: added `## Observability / Diagnostics` to S02-PLAN.md and `## Observability Impact` to T01-PLAN.md.

## Verification

1. Old star path absent from nav: `grep -q "M16 2L18 10L26 10" frontend/index.html` → exit 1 ✅
2. Old star path absent from app.js: `grep -q "M40 12L44 28L56 28" frontend/js/app.js` → exit 1 ✅
3. No "star" text in nav: `grep -q "star" frontend/index.html` → exit 1 ✅
4. House icon unchanged: `grep -q "M5 14L16 4L27 14V27H20V20H12V27H5V14Z" frontend/index.html` → exit 0 ✅
5. Pencil icon unchanged: `grep -q "M6 26L8 18L22 4L28 10L14 24L6 26Z" frontend/index.html` → exit 0 ✅
6. E2E tests: `.venv/bin/python -m pytest tests/test_e2e.py -x -q` → 14 passed ✅

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `grep -q "M16 2L18 10L26 10" frontend/index.html` | 1 | ✅ pass | <1s |
| 2 | `grep -q "M40 12L44 28L56 28" frontend/js/app.js` | 1 | ✅ pass | <1s |
| 3 | `grep -q "star" frontend/index.html` | 1 | ✅ pass | <1s |
| 4 | House icon path check | 0 | ✅ pass | <1s |
| 5 | Pencil icon path check | 0 | ✅ pass | <1s |
| 6 | `.venv/bin/python -m pytest tests/test_e2e.py -x -q` | 0 | ✅ pass | 17.3s |

*Slice check `grep -c "TestIconSemantics" tests/test_e2e.py` returns 0 — expected at T01; TestIconSemantics class is created in T02.*

## Diagnostics

- Inspect rendered icons: `grep "path d=" frontend/index.html` — dress-up nav path should contain `C` cubic-bezier commands, not `L` polygon lines.
- Browser DevTools: Elements → `<nav id="nav-bar">` → `<a href="#/dressup">` → SVG `<path>` — `d` attribute should start with `M13 4 C13 4`.
- Failure mode: malformed `d=` renders silently blank (icon disappears); detectable as empty circle background with no fill shape in the dress-up button.

## Deviations

The old wavy tail-curve accent `M28 58Q34 52 40 56Q46 52 52 58` in the 80×80 button was replaced rather than kept, as it conflicted visually with the new bifurcated tail design. The plan allowed this ("can be kept if it complements the new tail, or replaced with a unified design").

## Known Issues

None.

## Files Created/Modified

- `frontend/index.html` — Dress-up nav icon star path replaced with mermaid tail cubic-bezier paths (32×32 viewBox)
- `frontend/js/app.js` — renderHome() dress-up button star path replaced with mermaid tail paths (80×80 viewBox); old wavy accent replaced with stem midline accent
- `.gsd/milestones/M004/slices/S02/S02-PLAN.md` — Added `## Observability / Diagnostics` section and expanded Verification list (pre-flight fix)
- `.gsd/milestones/M004/slices/S02/tasks/T01-PLAN.md` — Added `## Observability Impact` section (pre-flight fix)
