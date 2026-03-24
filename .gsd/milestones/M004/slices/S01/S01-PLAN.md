# S01: Dress-Up → Coloring Pipeline + Hair Path Fix

**Goal:** Kid picks a mermaid in dress-up, taps "Color This!", and lands on the coloring canvas with that mermaid's B&W outline loaded. Hair hue-rotate recoloring only affects hair, not body/skin/tail.
**Demo:** Navigate to dress-up, select mermaid-3, tap "Color This!", see mermaid-3's outline loaded on the coloring canvas ready to paint. Change hair color and only hair changes.

## Must-Haves

- Hair paths in all 9 mermaid SVGs wrapped in `<g id="hair-group">` — hue-rotate targets `#hair-group` only (HAIR-01)
- 9 B&W outline SVGs exist at `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` (PIPE-03)
- "Color This!" button visible in dress-up view (PIPE-02)
- "Color This!" navigates to coloring canvas with active character's outline pre-loaded (PIPE-01)
- 107+ tests passing (105 existing + at least 2 new)

## Proof Level

- This slice proves: integration
- Real runtime required: yes (Playwright E2E tests against live server)
- Human/UAT required: yes (visual check that outlines look like the dress-up characters)

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_dressup.py tests/test_e2e.py -x -q` — all existing + new tests pass
- `test -f frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg && test -f frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` — outline assets exist
- `grep -q 'hair-group' frontend/assets/svg/dressup/mermaid-1.svg && grep -q 'hair-group' frontend/assets/svg/dressup/mermaid-9.svg` — hair group wrapper present
- `grep -q '#hair-group' frontend/js/dressup.js` — dressup.js targets hair-group for hue-rotate
- `grep -q 'Color This' frontend/js/app.js` — "Color This!" button exists in dress-up view

## Observability / Diagnostics

- Runtime signals: console.error on SVG fetch failure, error div rendered on load failure
- Inspection surfaces: Browser DevTools → check `#hair-group` element filter style, network tab for outline SVG loads
- Failure visibility: `.error` div displayed if outline SVG fails to load; existing `if (!resp.ok) throw` pattern catches HTTP errors
- Redaction constraints: none

## Integration Closure

- Upstream surfaces consumed: `frontend/js/coloring.js` — `initColoringCanvas(svgUrl, container)` API unchanged; `frontend/js/dressup.js` — `state.activeCharacter` already exported
- New wiring introduced in this slice: `app.js` router parses `character` query param from hash, new `renderColoringForCharacter()` function composes coloring UI for dress-up outlines
- What remains before the milestone is truly usable end-to-end: S02 (icon refresh), S03 (coloring pages 5-9 art), final deploy to GitHub Pages

## Tasks

- [x] **T01: Wrap hair paths in `<g id="hair-group">` and target for hue-rotate** `est:45m`
  - Why: HAIR-01 — hue-rotate currently applies to the entire SVG element, shifting colors on body/skin/tail. The clipPath already clips hair geometry at y=310, but dressup.js applies `filter: hue-rotate(Xdeg)` to the root `<svg>`, not just the hair paths. Wrapping clipped paths in a `<g id="hair-group">` and targeting that group for the filter isolates the color shift to hair only.
  - Files: `frontend/assets/svg/dressup/mermaid-{1-9}.svg`, `frontend/js/dressup.js`, `tests/test_dressup.py`
  - Do: In each of the 9 SVGs, wrap the 2 paths that have `clip-path="url(#hair-clip)"` in a `<g id="hair-group">...</g>`. In `dressup.js`, change `recolorActivePart()` to find `#hair-group` inside the container and apply `hue-rotate` filter to that element instead of the root SVG. Update `selectCharacter()` similarly — clear filter on `#hair-group` not root SVG. Update undo logic. Add a test that verifies hue-rotate is applied to `#hair-group` not the root SVG.
  - Verify: `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_dressup.py -x -q`
  - Done when: All 9 SVGs have `<g id="hair-group">`, dressup.js targets `#hair-group` for hue-rotate, existing dress-up tests pass, new hair-group test passes.

- [x] **T02: Create coloring outline assets for all 9 dress-up characters** `est:1h`
  - Why: PIPE-03 — the "Color This!" flow requires B&W outline SVGs matching each dress-up character. Per D002, these are pre-generated static assets (no runtime AI). This task creates the generation script and deploys 9 outline SVGs to `frontend/assets/svg/dressup-coloring/`.
  - Files: `scripts/generate_dressup_outlines.py`, `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg`, `tests/test_pipeline.py`
  - Do: Create `scripts/generate_dressup_outlines.py` that uses `COLORING_BASE_PROMPT + DRESSUP_CHARACTERS[i]['prompt_detail']` and the existing pipeline (generate PNG → vtracer trace to SVG). Create the `frontend/assets/svg/dressup-coloring/` directory, generate and place all 9 outline SVGs. If API key unavailable, create clean placeholder SVGs (simple B&W mermaid outlines at 1024x1024) that serve as valid coloring targets. Add asset existence tests to `tests/test_pipeline.py`.
  - Verify: `test -f frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg && test -f frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg && .venv/bin/python -m pytest tests/test_pipeline.py -x -q`
  - Done when: All 9 `mermaid-{1-9}-outline.svg` files exist in `frontend/assets/svg/dressup-coloring/`, each is >500 bytes, and asset existence tests pass.

- [x] **T03: Add "Color This!" button and dress-up → coloring routing** `est:1h`
  - Why: PIPE-01/PIPE-02 — connects dress-up and coloring into one creative flow. Kid taps "Color This!" and immediately sees their mermaid's outline on the coloring canvas.
  - Files: `frontend/js/app.js`, `frontend/css/style.css`, `tests/test_e2e.py`
  - Do: Add a "Color This!" button to the `renderDressUp()` HTML template (prominent, child-friendly, positioned below the color row). Wire the button to navigate to `#/coloring?character={activeCharacter}`. Update the router to parse `character` query param from the hash. Create a `renderColoringForCharacter(characterId)` function that builds the coloring UI (reuse `openColoringPage` pattern) loading `assets/svg/dressup-coloring/${characterId}-outline.svg`. Add a "Back to Dress Up" back button that returns to `#/dressup`. Style the "Color This!" button in `style.css`. Add E2E test: navigate to dress-up, select a character, click "Color This!", verify coloring canvas loads with the outline SVG.
  - Verify: `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q`
  - Done when: "Color This!" button visible in dress-up, clicking it navigates to coloring canvas with matching character outline, back button returns to dress-up, E2E test passes, 107+ total tests passing.

## Files Likely Touched

- `frontend/assets/svg/dressup/mermaid-{1-9}.svg`
- `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg`
- `frontend/js/app.js`
- `frontend/js/dressup.js`
- `frontend/css/style.css`
- `scripts/generate_dressup_outlines.py`
- `tests/test_dressup.py`
- `tests/test_e2e.py`
- `tests/test_pipeline.py`
