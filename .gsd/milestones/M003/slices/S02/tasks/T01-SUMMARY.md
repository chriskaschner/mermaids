---
id: T01
parent: S02
milestone: M003
provides:
  - 9-entry COLORING_PAGES in prompts.py with distinct hair/eyes/tail per page
  - 9-entry COLORING_PAGES in coloring.js with matching IDs and labels
  - Updated test assertions (9-page count, distinct styles, gallery >= 9)
  - CSS gallery layout fix enabling scrollable 9-item grid without element overlap
key_files:
  - src/mermaids/pipeline/prompts.py
  - frontend/js/coloring.js
  - tests/test_generate.py
  - tests/test_coloring.py
  - tests/test_floodfill_unit.py
  - src/mermaids/pipeline/generate.py
  - frontend/css/style.css
key_decisions:
  - Added max-height: 260px to .gallery-thumb to prevent aspect-ratio-driven overflow in scrollable grid
  - Added overflow: hidden and pointer-events: none to gallery thumb images to prevent intercept bugs
  - Changed .coloring-gallery from height:100%/align-content:center to height:100%/overflow-y:auto/align-content:start
patterns_established:
  - When expanding a gallery count, always verify the CSS grid layout handles the new item count without button overlap in Playwright viewport
observability_surfaces:
  - uv run pytest tests/test_generate.py::TestGenerateColoringPages -v (unit: count and distinctness)
  - uv run pytest tests/test_coloring.py::TestColoringGallery -v (E2E: gallery thumbnail count)
  - grep -c '"page-' src/mermaids/pipeline/prompts.py (expect 9)
  - grep -c '"page-' frontend/js/coloring.js (expect 9)
duration: ~40m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T01: Expand coloring pages to 9 with distinct hair/eyes/tail variety

**Expanded COLORING_PAGES from 4 to 9 entries in both prompts.py and coloring.js; fixed gallery CSS overflow; full suite passes with 103 tests.**

## What Happened

Executed all 5 planned steps plus one unplanned CSS fix:

1. **prompts.py** — Added 5 new entries (page-5-forest through page-9-starfish) each with distinct hair style, eye style, tail style, scene description, and explicit "single enclosed shape with clear black outline" language for hair and tail regions.

2. **coloring.js** — Added 5 matching entries with child-friendly labels: Kelp Forest, Treasure Chest, Jellyfish Meadow, Whirlpool Vortex, Starfish Beach.

3. **test_generate.py** — Renamed `test_generate_coloring_pages_produces_all_four` → `_all_nine`, updated assertion from `== 4` to `== 9`. Added `test_coloring_page_prompts_have_distinct_styles` asserting all 9 IDs unique and all `prompt_detail` values unique.

4. **test_coloring.py** — Updated gallery thumbnail assertion from `>= 4` to `>= 9`.

5. **generate.py** — Removed hardcoded "4" from docstring: "Generate all 4 coloring page PNGs" → "Generate all coloring page PNGs".

6. **Unplanned: test_floodfill_unit.py** — Found hardcoded `assert result["length"] == 4` for COLORING_PAGES JS array length. Updated to `== 9`.

7. **Unplanned: frontend/css/style.css** — The 9-item gallery (5 rows × tall buttons) caused Playwright click intercepts because CSS `aspect-ratio: 3/4` produced buttons ~821px tall in the Playwright viewport (1280×800), causing adjacent rows to overlap at click coordinates. Fixed by: (a) adding `max-height: 260px` to `.gallery-thumb` to bound button height, (b) adding `overflow: hidden` and `pointer-events: none` to gallery thumb images, (c) changing `.coloring-gallery` to `overflow-y: auto; align-content: start; box-sizing: border-box`.

## Verification

All slice verification checks pass:

- `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` → **2 passed** (nine-count + distinct styles)
- `uv run pytest tests/test_coloring.py::TestColoringGallery -v` → **1 passed** (≥9 thumbnails)
- `uv run pytest -q` → **103 passed** (exceeds 102+ target)
- `grep -c '"page-' src/mermaids/pipeline/prompts.py` → **9**
- `grep -c '"page-' frontend/js/coloring.js` → **9**
- `! grep -q "_initDebug" frontend/js/app.js` → NOT checked here (T02 scope)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` | 0 | ✅ pass | 0.34s |
| 2 | `uv run pytest tests/test_coloring.py::TestColoringGallery -v` | 0 | ✅ pass | 1.78s |
| 3 | `uv run pytest -q` | 0 | ✅ pass | 38.92s (103 passed) |
| 4 | `grep -c '"page-' src/mermaids/pipeline/prompts.py` | 0 | ✅ 9 | — |
| 5 | `grep -c '"page-' frontend/js/coloring.js` | 0 | ✅ 9 | — |

## Diagnostics

To inspect coloring page definitions:
- Python: `from mermaids.pipeline.prompts import COLORING_PAGES; print(len(COLORING_PAGES))`
- JS: `import('./js/coloring.js').then(m => console.log(m.COLORING_PAGES.length))`
- Gallery smoke-test: `uv run pytest tests/test_coloring.py::TestColoringGallery -v`

Runtime failure signal: if new SVG files for pages 5-9 are missing (`assets/svg/coloring/page-N-*.svg`), the gallery will show blank thumbnails but remain functional — existing 4 pages are clickable.

## Deviations

- **test_floodfill_unit.py** — The plan didn't mention this file, but it had a hardcoded `== 4` assertion for `COLORING_PAGES.length`. Updated to `== 9`.
- **frontend/css/style.css** — Not in the task plan. Required to fix gallery item overlap caused by `aspect-ratio: 3/4` producing overly tall buttons in the Playwright viewport (1280×800). Added `max-height: 260px` to `.gallery-thumb`, `overflow: hidden` + `pointer-events: none` to `.gallery-thumb img`, and `overflow-y: auto; align-content: start` to `.coloring-gallery`.

## Known Issues

- Pages 5-9 have no SVG files yet (`page-5-forest.svg` through `page-9-starfish.svg` don't exist). Art generation requires `uv run python scripts/generate_coloring.py` + `scripts/trace_all.py` with an OpenAI API key. This is expected — noted in S02 Integration Closure.
- `_initDebug` still present in `app.js` — that's T02 scope.

## Files Created/Modified

- `src/mermaids/pipeline/prompts.py` — Expanded COLORING_PAGES from 4 to 9 entries with distinct hair/eyes/tail per page
- `frontend/js/coloring.js` — Expanded COLORING_PAGES from 4 to 9 entries with matching IDs and child-friendly labels
- `tests/test_generate.py` — Renamed test, updated count assertion (4→9), added distinctness test
- `tests/test_coloring.py` — Updated gallery thumbnail assertion (>= 4 → >= 9)
- `tests/test_floodfill_unit.py` — Updated COLORING_PAGES length assertion (4→9)
- `src/mermaids/pipeline/generate.py` — Updated docstring removing hardcoded "4"
- `frontend/css/style.css` — Fixed gallery grid layout: max-height on buttons, overflow-y scroll, pointer-events none on imgs
