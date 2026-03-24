# S01: Dress Up Art Rework — UAT

**Milestone:** M003
**Written:** 2026-03-23

## UAT Type

- UAT mode: mixed (artifact-driven test verification + live-runtime browser checks)
- Why this mode is sufficient: 14 Playwright E2E tests cover gallery swap, recolor, undo, and completion mechanics. Browser visual checks confirm AI art quality and hue-rotate on diverse skin tones.

## Preconditions

- All dependencies installed: `uv sync`
- Playwright browsers installed: `uv run playwright install chromium`
- Local server available: `uv run python -m http.server 8080 --directory frontend`

## Smoke Test

Run `uv run pytest tests/test_dressup.py -v` — all 14 tests must pass. This confirms the gallery renders, character swapping works, recoloring applies, and undo restores state.

## Test Cases

### 1. Full Test Suite Passes

1. Run `uv run pytest -q`
2. **Expected:** 102 passed, 0 failed, 0 errors

### 2. Gallery Shows 9 Character Buttons

1. Start local server: `uv run python -m http.server 8080 --directory frontend`
2. Navigate to `http://localhost:8080#/dressup`
3. Count character buttons in the selection panel
4. **Expected:** 9 buttons visible, first button (mermaid-1) is selected by default

### 3. Character Swap Replaces Entire SVG

1. On the dress-up view, click the mermaid-3 button
2. Check the displayed SVG content
3. **Expected:** The `#mermaid-svg` element now shows mermaid-3's SVG paths. The `.char-btn.selected` dataset.character should be "mermaid-3". No remnant of the previous character's paths.

### 4. Hue-Rotate Recoloring Applies

1. On the dress-up view with any character active, click a color swatch (e.g., hot pink)
2. Inspect `document.getElementById('mermaid-svg')?.style?.filter`
3. **Expected:** Returns `"hue-rotate(Xdeg)"` where X corresponds to the swatch color (e.g., 330 for hot pink). All colors in the mermaid shift proportionally.

### 5. Recoloring Works on Dark-Skinned Character

1. Click the mermaid-4 button (dark-skinned character)
2. Click the teal color swatch
3. **Expected:** The entire character recolors to teal tones. `svg.style.filter` returns `"hue-rotate(180deg)"`. No parts are excluded or left unchanged — hue-rotate shifts all fills uniformly.

### 6. Undo Reverts Last Action

1. With mermaid-1 selected, click mermaid-5 to swap
2. Click the undo button
3. **Expected:** mermaid-1 is restored. `.char-btn.selected` dataset.character is "mermaid-1".
4. Apply a color recolor, then click undo
5. **Expected:** `svg.style.filter` returns empty string (no filter active)

### 7. Celebration Sparkle on Completion

1. Click any character button other than the default
2. **Expected:** After a character change, the celebration sparkle animation triggers (test `test_celebration_sparkle` verifies a sparkle element appears)

### 8. Touch Targets Are 60pt+

1. Inspect all `.char-btn` elements
2. **Expected:** Each button has width and height ≥ 60px (iPad-friendly touch targets)

### 9. Pipeline Region Masks Are Non-Overlapping

1. Run `uv run pytest tests/test_masks.py::TestRegions -v`
2. **Expected:** 3 tests pass — 4 categories present, no bounding box overlap, hair y2 (290) < tail y1 (550) confirming DEBT-03 fix

### 10. SVG Assembly Produces Valid Structure

1. Run `uv run pytest tests/test_assemble.py -v`
2. **Expected:** All 9 tests pass — valid SVG, mermaid-svg ID, viewBox, background stripped, content paths preserved, characters deployed, mermaid-1 copied as default

### 11. All Character SVGs Present on Disk

1. Run `ls frontend/assets/svg/dressup/mermaid-*.svg | wc -l`
2. **Expected:** 9 files (mermaid-1.svg through mermaid-9.svg)
3. Run `ls -la frontend/assets/svg/mermaid.svg`
4. **Expected:** File exists, non-zero size (~30KB)

## Edge Cases

### No Network Errors on Character Load

1. Open browser dev tools Network tab
2. Navigate to `http://localhost:8080#/dressup`
3. Click through all 9 character buttons
4. **Expected:** No 404 errors on any `assets/svg/dressup/mermaid-*.svg` fetch

### Mermaid SVG Has AI Art (Not Stubs)

1. Navigate to dress-up view
2. Run `document.querySelectorAll('#mermaid-svg path').length`
3. **Expected:** > 10 paths (AI-generated art has many paths; geometric stubs would have < 10)

### Error State on Missing SVG

1. Temporarily rename `frontend/assets/svg/mermaid.svg`
2. Navigate to `http://localhost:8080#/dressup`
3. **Expected:** `#app` shows `<div class="error">Could not load mermaid.</div>`
4. Restore the file after testing

## Failure Signals

- Any `uv run pytest tests/test_dressup.py` failure — dress-up E2E test regression
- Network 404 on `assets/svg/dressup/mermaid-*.svg` — character SVG file missing
- `svg.style.filter` empty after clicking a color swatch — recoloring broken
- `#app .error` div visible — mermaid.svg failed to load
- `path_count < 10` on any character — SVG contains geometric stubs, not AI art
- Any test in `test_masks.py::TestRegions` failing — region overlap regression (DEBT-03)

## Not Proven By This UAT

- Coloring page integration — deferred to S02
- Multi-layer part-swapping (original architecture) — superseded by gallery approach; pipeline infrastructure retained but frontend doesn't use it
- Accessories category in frontend — pipeline has acc region masks but gallery approach doesn't expose per-category swapping
- Production deployment verification — these tests run against local server only
- WebKit-specific sparkle behavior (DEBT-02) — 2 pre-existing WebKit failures remain

## Notes for Tester

- The GSD plans describe a multi-layer part-swapping architecture. **This was superseded.** The actual implementation is a 9-character gallery. Read KNOWLEDGE.md's "Architecture Pivot" entry for context.
- Recoloring uses CSS `hue-rotate`, NOT fill manipulation. If you inspect individual `path[fill]` attributes, they will NOT change when recoloring — this is correct behavior.
- mermaid-4 is specifically important to test because it's the dark-skinned character that broke the old fill-manipulation approach.
- Touch target tests use 60px as the threshold, matching iPad usability requirements.
