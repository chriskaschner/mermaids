---
estimated_steps: 4
estimated_files: 2
skills_used:
  - frontend-design
  - best-practices
---

# T01: Replace dress-up star icons with mermaid tail SVG paths

**Slice:** S02 — Icon Refresh
**Milestone:** M004

## Description

Replace the generic 5-pointed star SVG icon used for "Dress Up" in both the nav bar (`index.html`) and the home screen activity button (`app.js` `renderHome()`) with a bifurcated mermaid tail icon. This is a pure SVG path replacement — no CSS, routing, or JS behavior changes.

The coloring pencil and home house icons are already semantically correct and must not be changed.

## Steps

1. **Design a 32×32 bifurcated mermaid tail SVG** — Create 2-3 `<path>` elements that form a recognizable mermaid tail fin (Y-fork / bifurcated fan shape). Use the existing dress-up color scheme: stroke `#c47ed0`, fill `#f0d4f5`. The tail should be visually distinct from the house and pencil icons at nav-bar size. Example approach: a narrow stem from ~y8 to ~y20, then two curved lobes splitting left and right to ~y28, with a filled area between the lobes.

2. **Replace the star path in `frontend/index.html`** (line ~24) — Find the dress-up nav icon `<a href="#/dressup" ...>` and replace its `<svg>` contents. The current star path is:
   ```
   <path d="M16 2L18 10L26 10L20 15L22 23L16 18L10 23L12 15L6 10L14 10Z" stroke="#c47ed0" stroke-width="2" fill="#f0d4f5"/>
   ```
   Replace with the mermaid tail paths. Keep the `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">` wrapper unchanged.

3. **Replace the star path in `frontend/js/app.js` `renderHome()`** (~line 36-38) — In the dress-up activity button's 80×80 SVG, replace the star path:
   ```
   <path d="M40 12L44 28L56 28L46 38L50 54L40 44L30 54L34 38L24 28L36 28Z" fill="#c47ed0" opacity="0.8"/>
   ```
   with a mermaid tail scaled to the 80×80 viewBox (centered in the circle). Keep the circle background `<circle cx="40" cy="40" r="36" .../>`. The existing tail-curve line `<path d="M28 58Q34 52 40 56Q46 52 52 58" .../>` can be kept if it complements the new tail, or replaced with a unified design. The result should be a clear mermaid tail icon inside the circle.

4. **Verify no regressions** — Run `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q` to confirm all existing E2E tests still pass (tap targets, navigation, etc.).

## Must-Haves

- [ ] Nav bar dress-up icon shows a mermaid tail, not a star
- [ ] Home screen dress-up button shows a mermaid tail inside the circle, not a star
- [ ] Home house icon unchanged (`M5 14L16 4L27 14V27H20V20H12V27H5V14Z`)
- [ ] Coloring pencil icon unchanged (`M6 26L8 18L22 4L28 10L14 24L6 26Z`)
- [ ] No CSS classes, JS routing, or event handler changes — SVG path data only
- [ ] Existing E2E tests pass without modification

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q` — all existing tests pass
- `grep -q "M16 2L18 10L26 10" frontend/index.html` exits 1 (old star path removed from nav)
- `grep -q "M40 12L44 28L56 28" frontend/js/app.js` exits 1 (old star path removed from home button)

## Observability Impact

**What changes:** The SVG `d=` attribute content inside `<a href="#/dressup">` in `index.html` and inside `renderHome()`'s dress-up `<a>` in `app.js`. No JS behavior, CSS classes, routing, or event handlers change.

**How a future agent inspects this task:**
- `grep "path d=" frontend/index.html` — confirms mermaid tail cubic-bezier paths (containing `C`) are present for the dress-up nav icon, and no polygon star coordinates (`L18 10L26 10`) remain.
- `grep "path d=" frontend/js/app.js` — same check for the home screen button.
- Open browser DevTools → Elements → `<nav id="nav-bar">` → expand dress-up `<a>` → confirm SVG has `<path>` with `C` curve commands.

**Failure state:** A malformed SVG path `d=` attribute renders silently blank — the icon circle shows but the tail shape is invisible. Detectable by: (1) visual inspection shows empty circle for dress-up button, (2) `document.querySelector('[aria-label="Dress Up"] svg path')` returns null or a path with an empty/invalid `d`.

**No metrics, logs, or structured output** are produced by this task — it is a purely static asset change.

## Inputs

- `frontend/index.html` — Contains the nav bar with 3 inline SVG icons (lines 14-31). The dress-up star path at line ~24 needs replacement.
- `frontend/js/app.js` — Contains `renderHome()` (lines ~28-51) with the dress-up activity button's 80×80 inline SVG. The star path at line ~36 needs replacement.

## Expected Output

- `frontend/index.html` — Dress-up nav icon SVG paths changed from star to mermaid tail
- `frontend/js/app.js` — Dress-up home button SVG paths changed from star to mermaid tail
