---
estimated_steps: 5
estimated_files: 4
skills_used:
  - test
  - best-practices
---

# T03: Add "Color This!" button and dress-up → coloring routing

**Slice:** S01 — Dress-Up → Coloring Pipeline + Hair Path Fix
**Milestone:** M004

## Description

Wire the dress-up → coloring pipeline in the frontend. Add a prominent "Color This!" button to the dress-up view that navigates to the coloring canvas with the active character's B&W outline pre-loaded. Per decision D003, this bypasses the coloring gallery entirely — direct button-to-canvas flow.

The routing uses a `character` query parameter in the hash: `#/coloring?character=mermaid-3`. The router parses this and calls a new `renderColoringForCharacter(characterId)` function that builds the coloring UI (identical to `openColoringPage` but loads from `assets/svg/dressup-coloring/{characterId}-outline.svg`).

The 9 outline SVGs already exist at `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` (created in T02).

## Steps

1. **Add "Color This!" button to `renderDressUp()` in `frontend/js/app.js`**: Insert a button after the `.color-row` div inside `.selection-panel`. The button should be prominent and child-friendly:
   ```html
   <button class="color-this-btn" aria-label="Color This Mermaid!">🎨 Color This!</button>
   ```
   Wire the button click to read `state.activeCharacter` from dressup.js (already imported as part of dressup module — add `state` to the import) and navigate: `window.location.hash = '#/coloring?character=' + state.activeCharacter;`
   
   **Import change in app.js**: Add `state as dressupState` to the existing import from `dressup.js`. The import line currently imports `{ initDressUp, resetState, CHARACTERS, COLORS as DRESSUP_COLORS }`. Add `state as dressupState`.

2. **Update the router in `frontend/js/app.js`**: Modify the `router()` function to parse query parameters from the hash. The hash format is `#/coloring?character=mermaid-3`. Parse by splitting on `?`, then extract `character` param. If `hash === "coloring"` and `character` param exists, call `renderColoringForCharacter(character)` instead of `renderColoring()`.

3. **Create `renderColoringForCharacter(characterId)` in `frontend/js/app.js`**: This function builds the same coloring UI as `openColoringPage()` but:
   - Loads SVG from `assets/svg/dressup-coloring/${characterId}-outline.svg`
   - "Back" button navigates to `#/dressup` (not back to gallery)
   - Otherwise identical: canvas + SVG overlay + tool buttons + color swatches + undo
   - Reuse the coloring.js API: `initColoringCanvas()`, `handleCanvasTap()`, `strokeStart/Move/End()`, etc.
   - Include the same error handling pattern: `if (!resp.ok) throw new Error(...)` per KNOWLEDGE.md guidance

4. **Style the "Color This!" button in `frontend/css/style.css`**: Add `.color-this-btn` styles — large touch target (min 60px height), full width of selection panel, rounded corners, bright palette/paint color (e.g., coral/pink), bold text, child-friendly. Add a subtle hover/active state.

5. **Add E2E test in `tests/test_e2e.py`**: Add test class `TestDressUpToColoring` with:
   - `test_color_this_button_visible`: Navigate to dress-up, verify "Color This!" button is visible
   - `test_color_this_navigates_to_coloring_canvas`: Navigate to dress-up, click "Color This!", verify coloring canvas is visible (`#coloring-canvas` or `.coloring-view` present), verify the URL contains `character=mermaid-1` (default character)
   - `test_color_this_with_different_character`: Navigate to dress-up, select mermaid-3 (click the 3rd char-btn), click "Color This!", verify URL contains `character=mermaid-3`

## Must-Haves

- [ ] "Color This!" button visible in dress-up view
- [ ] Clicking "Color This!" navigates to `#/coloring?character={activeCharacter}`
- [ ] Router parses `character` query param and calls `renderColoringForCharacter()`
- [ ] `renderColoringForCharacter()` loads the correct outline SVG and initializes coloring canvas
- [ ] "Back" button in character coloring view navigates to `#/dressup`
- [ ] E2E tests verify the full flow
- [ ] All existing E2E tests still pass (no routing regressions)

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py -x -q` — all E2E tests pass including new ones
- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/ -x -q` — full test suite passes, 107+ tests total
- `grep -q 'Color This' frontend/js/app.js` — button text exists
- `grep -q 'renderColoringForCharacter' frontend/js/app.js` — new function exists

## Inputs

- `frontend/js/app.js` — current router and view renderers (router, renderDressUp, openColoringPage to use as pattern)
- `frontend/js/dressup.js` — exports `state.activeCharacter` (already exported, just needs import in app.js)
- `frontend/js/coloring.js` — `initColoringCanvas(svgUrl, container)` API used by the new renderer
- `frontend/css/style.css` — existing styles for coloring-view, selection-panel, activity buttons
- `frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` — outline SVG assets created by T02
- `tests/test_e2e.py` — existing E2E tests and fixtures (app_page fixture pattern)

## Expected Output

- `frontend/js/app.js` — updated with "Color This!" button, router query param parsing, `renderColoringForCharacter()`
- `frontend/css/style.css` — updated with `.color-this-btn` styles
- `tests/test_e2e.py` — updated with `TestDressUpToColoring` test class (2-3 new tests)
