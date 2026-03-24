---
id: S02
parent: M003
milestone: M003
provides:
  - 9 coloring page definitions in prompts.py with distinct hair/eyes/tail per page and explicit closed-outline prompt language
  - 9 matching entries in coloring.js with child-friendly labels
  - Scrollable gallery CSS layout supporting 9 items without Playwright hit-test overlap
  - Debug overlay (_initDebug, ?debug=1, triple-tap) fully removed from app.js
  - DEBT-02 (WebKit sparkle failures) formally confirmed fixed
  - 103 tests passing across all suites
requires:
  - slice: S01
    provides: Base app architecture, dress-up gallery pattern, CSS grid layout conventions
affects:
  - S03
key_files:
  - src/mermaids/pipeline/prompts.py
  - frontend/js/coloring.js
  - frontend/js/app.js
  - frontend/css/style.css
  - tests/test_generate.py
  - tests/test_coloring.py
  - tests/test_floodfill_unit.py
  - src/mermaids/pipeline/generate.py
key_decisions:
  - Added max-height 260px to .gallery-thumb to prevent aspect-ratio-driven overflow in 9-item grid
  - Changed .coloring-gallery from centered fixed-height to scrollable (overflow-y auto, align-content start)
  - Added pointer-events none to gallery thumb images to prevent Playwright hit-test intercepts
  - Removed entire _initDebug function and all activation wiring in a single pass without replacement stubs
  - Coloring page flood-fill quality (COLR-02/COLR-03) verified via structural prompt checks — prompts explicitly request closed outlines; actual fill quality verified visually after art generation
patterns_established:
  - When expanding a gallery item count, always verify CSS grid handles the new count in the Playwright viewport (1280×800) — aspect-ratio can produce oversized items causing row overlap
  - After removing dead code, run grep-negation checks for all related symbols before running the full test suite — fast local confirmation before spending 50s on E2E
observability_surfaces:
  - "grep -c '\"page-' src/mermaids/pipeline/prompts.py → expect 9"
  - "grep -c '\"page-' frontend/js/coloring.js → expect 9"
  - "grep -q '_initDebug' frontend/js/app.js → must exit 1 (absent)"
  - "uv run pytest tests/test_generate.py::TestGenerateColoringPages -v → 2 passed"
  - "uv run pytest tests/test_coloring.py::TestColoringGallery -v → 1 passed"
  - "uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit → 2 passed (DEBT-02)"
  - "uv run pytest -q → 103 passed"
drill_down_paths:
  - .gsd/milestones/M003/slices/S02/tasks/T01-SUMMARY.md
  - .gsd/milestones/M003/slices/S02/tasks/T02-SUMMARY.md
duration: ~50m
verification_result: passed
completed_at: 2026-03-23
---

# S02: Coloring Art Rework

**Coloring gallery expanded from 4 to 9 pages with distinct hair/eyes/tail variety per page, debug overlay removed, WebKit sparkle tests confirmed fixed, all 103 tests passing.**

## What Happened

Two tasks delivered the full slice goal:

**T01 (Expand coloring pages to 9)** added 5 new coloring page definitions (page-5-forest through page-9-starfish) to both `prompts.py` and `coloring.js`. Each new page has a distinct hair style (kelp-draped, ribbon-braided, etc.), eye style (emerald wide, sapphire curious, etc.), and tail style (leafy fern, map-engraved, etc.) with explicit "single enclosed shape with clear black outline" prompt language for hair and tail regions — addressing COLR-01, COLR-02, and COLR-03. Tests were updated: `test_generate.py` now asserts 9 pages and verifies all prompts have distinct style descriptions; `test_coloring.py` asserts ≥9 gallery thumbnails; `test_floodfill_unit.py` was discovered to have a hardcoded `== 4` assertion that was updated to `== 9`.

An unplanned CSS fix was required: the 9-item gallery in Playwright's 1280×800 viewport produced buttons ~821px tall due to `aspect-ratio: 3/4`, causing adjacent grid rows to overlap at click coordinates. Fixed by adding `max-height: 260px` to `.gallery-thumb`, `overflow-y: auto` + `align-content: start` to `.coloring-gallery`, and `pointer-events: none` to gallery thumb images.

**T02 (Remove debug overlay)** deleted the entire `_initDebug()` function (~85 lines), the `?debug=1` URL parameter activation block, and the triple-tap wiring (homeNavIcon, tapCount, tapTimer, capture-phase click listener) from `app.js`. The DOMContentLoaded handler now contains only hash-routing bootstrap. WebKit sparkle tests (2/2) confirmed DEBT-02 was already resolved with no code changes needed.

## Verification

All slice-level verification checks pass:

| Check | Result |
|-------|--------|
| `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` | ✅ 2 passed |
| `uv run pytest tests/test_coloring.py::TestColoringGallery -v` | ✅ 1 passed |
| `uv run pytest -q` | ✅ 103 passed in 43s |
| `grep -c '"page-' src/mermaids/pipeline/prompts.py` | ✅ 9 |
| `grep -c '"page-' frontend/js/coloring.js` | ✅ 9 |
| `! grep -q "_initDebug" frontend/js/app.js` | ✅ absent |
| `! grep -q "debug=1" frontend/js/app.js` | ✅ absent |
| `! grep -q "tapCount" frontend/js/app.js` | ✅ absent |
| `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit` | ✅ 2 passed (DEBT-02) |

## New Requirements Surfaced

- none

## Deviations

- **test_floodfill_unit.py** — Not in the task plan. Had a hardcoded `== 4` assertion for `COLORING_PAGES.length` that needed updating to `== 9`.
- **frontend/css/style.css** — Not in the task plan. Required to fix gallery item overlap caused by `aspect-ratio: 3/4` producing oversized buttons in the Playwright viewport. Added `max-height: 260px` to `.gallery-thumb`, scroll/start alignment to `.coloring-gallery`, and `pointer-events: none` to gallery thumb images.
- **S02-PLAN.md** — Observability/Diagnostics section was added to the plan during T02 execution to satisfy pre-flight gap requirements.

## Known Limitations

- **Pages 5-9 have no SVG art files.** Files `page-5-forest.svg` through `page-9-starfish.svg` don't exist yet. Art generation requires `uv run python scripts/generate_coloring.py` + `scripts/trace_all.py` with an OpenAI API key. The gallery renders blank thumbnails for missing pages but remains functional — the existing 4 pages work normally.
- **COLR-02/COLR-03 (closed hair/tail outlines)** verified at the prompt level only — prompts explicitly request closed outlines. Actual fill quality depends on AI art generation output and must be verified visually after running the generation pipeline.

## Follow-ups

- Run art generation pipeline for pages 5-9 when OpenAI API key is available: `uv run python scripts/generate_coloring.py && scripts/trace_all.py`
- S03 (Cleanup & Stability) should verify the generated SVGs for pages 5-9 actually have closed fill regions for hair and tail

## Files Created/Modified

- `src/mermaids/pipeline/prompts.py` — Expanded COLORING_PAGES from 4 to 9 entries with distinct hair/eyes/tail per page
- `frontend/js/coloring.js` — Expanded COLORING_PAGES from 4 to 9 entries with matching IDs and child-friendly labels
- `tests/test_generate.py` — Updated count assertion (4→9), added distinctness test
- `tests/test_coloring.py` — Updated gallery thumbnail assertion (≥4 → ≥9)
- `tests/test_floodfill_unit.py` — Updated COLORING_PAGES length assertion (4→9)
- `src/mermaids/pipeline/generate.py` — Updated docstring removing hardcoded "4"
- `frontend/css/style.css` — Fixed gallery grid layout: max-height on buttons, overflow-y scroll, pointer-events none on imgs
- `frontend/js/app.js` — Removed _initDebug() function (~85 lines), ?debug=1 activation, triple-tap wiring

## Forward Intelligence

### What the next slice should know
- The coloring gallery now has 9 entries but only 4 have actual SVG art. Pages 5-9 will show blank thumbnails until the generation pipeline is run. This is by design — the frontend/backend definitions are in place, just awaiting art assets.
- The CSS gallery layout uses `max-height: 260px` + `overflow-y: auto` to handle 9 items. If S03 adds more items or changes the grid, this constraint must be preserved or the Playwright viewport will produce click-intercept failures.
- app.js is now cleaner — the DOMContentLoaded handler only contains hash-routing bootstrap. Any new initialization should go there cleanly.

### What's fragile
- **Gallery CSS at scale** — The `max-height: 260px` constraint on `.gallery-thumb` is tuned for 9 items in a 2-column grid within 1280×800. Adding more items or changing the grid columns could break the layout in Playwright tests even if it looks fine visually.
- **Coloring page art quality** — COLR-02/COLR-03 (closed outlines for hair/tail) are enforced only via prompt language. The AI model may not always produce perfectly closed shapes. Visual verification after generation is essential.

### Authoritative diagnostics
- `uv run pytest -q` → 103 passed is the baseline. Any regression should be investigated immediately.
- `grep -c '"page-' src/mermaids/pipeline/prompts.py` → 9 confirms page count. Cross-check with `frontend/js/coloring.js`.
- `grep -q "_initDebug" frontend/js/app.js && echo REGRESSION || echo OK` → instant check for debug overlay re-introduction.

### What assumptions changed
- **Assumed test_floodfill_unit.py wouldn't need changes** — It had a hardcoded `== 4` for COLORING_PAGES length that had to be updated to `== 9`. When expanding array sizes, always grep the full test suite for hardcoded count assertions.
- **Assumed CSS gallery would handle 9 items** — It didn't. The aspect-ratio + fixed-height container combination produced oversized items. Always test gallery expansions in the actual Playwright viewport dimensions.