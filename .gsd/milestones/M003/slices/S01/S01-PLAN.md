# S01: Dress Up Art Rework

**Goal:** Rework the art generation pipeline from "each variant is a full character" to "one base body + swappable isolated parts.
**Demo:** Rework the art generation pipeline from "each variant is a full character" to "one base body + swappable isolated parts.

## Must-Haves


## Tasks

- [x] **T01: 08-dress-up-art-rework 01** `est:25min`
  - Rework the art generation pipeline from "each variant is a full character" to "one base body + swappable isolated parts." Add eyes as a new category. Redesign region masks so hair, eyes, tail, and accessories do not overlap (fixes DEBT-03). Update SVG assembly to produce multi-layer stacked `<use>` structure.

Purpose: The current pipeline generates 9 full-character variants where each is a complete mermaid. The new approach generates 1 static base body + 12 isolated part variants (3 per category), assembled into an SVG with 5 `<use>` layers that can be swapped independently.

Output: Updated pipeline modules (prompts.py, edit.py, assemble.py) and passing tests.
- [x] **T02: 08-dress-up-art-rework 02**
  - Rework the dress-up frontend from "swap between full characters" to "swap individual parts independently." Add eyes as a new category tab. Change recoloring to apply per-part (active category only). Update E2E tests.

Purpose: The current UI treats each variant as a complete character -- clicking "hair-2" shows an entirely different mermaid, not just different hair. The new approach has one persistent body with hair/eyes/tail/acc swapping independently via separate `<use>` elements.

Output: Updated dressup.js (multi-part swap logic), app.js (5-tab UI), and passing E2E tests.
- [x] **T03: 08-dress-up-art-rework 03**
  - Delete old dress-up assets, run the updated pipeline to generate a fresh base mermaid + 12 isolated part variants, trace to SVG, assemble the multi-layer mermaid.svg, and deploy to frontend. Visual verification by user on real device.

Purpose: The pipeline code (Plan 01) and frontend code (Plan 02) are ready but the app still has old single-character SVG assets. This plan generates the actual AI art, assembles it, deploys it, and gets user visual approval.

Output: New mermaid.svg with multi-layer structure, 12 preview thumbnails, working dress-up on live site.

- [x] **T04: Fix hair paths that bleed beyond hair region** `est:25min`
  - Clip or redraw the hair paths in all 9 mermaid SVGs (mermaid-1 through mermaid-9) so they are bounded to the visible hair zone. Currently, vtracer-traced hair paths (path[0] and path[1] in most characters) span y 59–970, covering the entire body/tail area behind them. When CSS hue-rotate is applied to recolor, these oversized hair paths shift color in regions the user perceives as skin or tail.

Purpose: Per user override — the current hair shapes make hue-rotate recoloring unusable because changing hair color visually changes everything. Bounding hair paths to their visible region (~y 0–300) isolates the recolor effect to just the hair.

Output: Updated mermaid-{1..9}.svg files in frontend/assets/svg/dressup/ with hair paths clipped to the hair zone. Hue-rotate recoloring visually affects only the intended region. All existing tests still pass.

## Observability / Diagnostics

- **Test pass rate:** `uv run pytest tests/test_dressup.py -v` — 14 E2E tests covering gallery, recolor, undo, sparkle.
- **Server:** `uv run python -m http.server 8080 --directory frontend` at `http://localhost:8080#/dressup`.
- **Console 404s:** Any `assets/svg/dressup/mermaid-*.svg` 404 means a character SVG is missing from `frontend/assets/svg/dressup/`.
- **Recolor signal:** `document.getElementById('mermaid-svg')?.style?.filter` — should return `hue-rotate(Xdeg)` after clicking a color swatch; empty string if no recolor applied.
- **Character swap signal:** `document.querySelector('.char-btn.selected')?.dataset?.character` — reflects the active character.
- **Failure path:** If `renderDressUp()` fails, `#app` shows `<div class="error">Could not load mermaid.</div>` — check network tab for the `assets/svg/mermaid.svg` fetch.
- **Redaction:** No sensitive data in any SVG or JS assets.

## Files Likely Touched

- `src/mermaids/pipeline/prompts.py`
- `src/mermaids/pipeline/edit.py`
- `src/mermaids/pipeline/assemble.py`
- `tests/test_masks.py`
- `tests/test_assemble.py`
- `frontend/js/dressup.js`
- `frontend/js/app.js`
- `tests/test_dressup.py`
- `assets/generated/png/dressup/base/mermaid-base.png`
- `assets/generated/png/dressup/parts/*.png`
- `assets/generated/svg/dressup/*.svg`
- `frontend/assets/svg/mermaid.svg`
- `frontend/assets/svg/dressup/*.svg`
