# S02: Coloring Art Rework — UAT

**Milestone:** M003
**Written:** 2026-03-23

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: All deliverables are code-level (data definitions, test assertions, dead code removal) verifiable via grep and pytest. No runtime server or human interaction needed.

## Preconditions

- Working directory: project root with `.venv` active
- `uv` installed and functional
- Playwright browsers installed (`uv run playwright install`)
- No OpenAI API key required (tests use mocked/existing assets)

## Smoke Test

```bash
uv run pytest -q
```
Expected: 103 passed. If fewer, investigate before proceeding.

## Test Cases

### 1. Coloring pages expanded to 9 in Python

1. Run: `grep -c '"page-' src/mermaids/pipeline/prompts.py`
2. **Expected:** Output is `9`
3. Run: `uv run python -c "from mermaids.pipeline.prompts import COLORING_PAGES; print(len(COLORING_PAGES))"`
4. **Expected:** Output is `9`

### 2. Coloring pages expanded to 9 in JavaScript

1. Run: `grep -c '"page-' frontend/js/coloring.js`
2. **Expected:** Output is `9`

### 3. Each page has distinct hair/eyes/tail styles

1. Run: `uv run pytest tests/test_generate.py::TestGenerateColoringPages::test_coloring_page_prompts_have_distinct_styles -v`
2. **Expected:** 1 passed — all 9 page IDs are unique, all `prompt_detail` values are unique

### 4. Page count test updated

1. Run: `uv run pytest tests/test_generate.py::TestGenerateColoringPages::test_generate_coloring_pages_produces_all_nine -v`
2. **Expected:** 1 passed — generates exactly 9 results

### 5. Gallery shows 9 thumbnails in E2E

1. Run: `uv run pytest tests/test_coloring.py::TestColoringGallery -v`
2. **Expected:** 1 passed — gallery renders ≥9 thumbnail buttons

### 6. Flood-fill unit test updated

1. Run: `uv run pytest tests/test_floodfill_unit.py -v -k "COLORING_PAGES"`
2. **Expected:** Tests pass with COLORING_PAGES.length == 9 (not 4)

### 7. Debug overlay fully removed (DEBT-01)

1. Run: `grep -q "_initDebug" frontend/js/app.js && echo FAIL || echo PASS`
2. **Expected:** `PASS`
3. Run: `grep -q "debug=1" frontend/js/app.js && echo FAIL || echo PASS`
4. **Expected:** `PASS`
5. Run: `grep -q "tapCount" frontend/js/app.js && echo FAIL || echo PASS`
6. **Expected:** `PASS`

### 8. WebKit sparkle tests pass (DEBT-02)

1. Run: `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit`
2. **Expected:** 2 passed (sparkle trigger + cleanup)

### 9. Full test suite passes

1. Run: `uv run pytest -q`
2. **Expected:** 103 passed, 0 failed

### 10. Prompts request closed outlines for hair and tail (COLR-02, COLR-03)

1. Run: `grep -c "enclosed.*outline\|outline.*enclosed\|closed.*outline\|outline.*closed" src/mermaids/pipeline/prompts.py`
2. **Expected:** Count ≥ 9 (each page's prompt mentions enclosed/closed outlines for hair and tail)

## Edge Cases

### Gallery CSS with 9 items in constrained viewport

1. Run: `grep "max-height" frontend/css/style.css | grep gallery`
2. **Expected:** `.gallery-thumb` has `max-height: 260px` — prevents aspect-ratio overflow
3. Run: `grep "overflow-y" frontend/css/style.css | grep -i auto`
4. **Expected:** `.coloring-gallery` has `overflow-y: auto` — enables scrolling

### No regression in dress-up E2E tests

1. Run: `uv run pytest tests/test_e2e.py -v`
2. **Expected:** 10 passed on Chromium — no regression from app.js changes

### Blank thumbnails for missing pages 5-9

1. Verify: `ls assets/svg/coloring/page-5-* 2>/dev/null || echo "No page-5 SVGs (expected)"`
2. **Expected:** "No page-5 SVGs (expected)" — pages 5-9 have no art yet, which is expected. The gallery shows blank thumbnails but remains functional.

## Failure Signals

- `uv run pytest -q` returns fewer than 103 passed → regression in test suite
- `grep -q "_initDebug" frontend/js/app.js` exits 0 → debug overlay was re-introduced
- `grep -c '"page-' src/mermaids/pipeline/prompts.py` returns anything other than 9 → page definitions out of sync
- Playwright "element intercepts pointer events" error in coloring gallery tests → CSS max-height constraint was removed or gallery item count changed
- WebKit sparkle tests fail → DEBT-02 regression

## Not Proven By This UAT

- **Visual quality of AI-generated art for pages 5-9** — No SVG files exist yet for the 5 new pages. Art generation requires an OpenAI API key and running the pipeline scripts. The prompt definitions are verified but actual art output is not.
- **Flood-fill correctness on new pages** — COLR-02/COLR-03 are verified at the prompt level (outlines requested). Whether the AI actually produces perfectly closed shapes depends on generation output.
- **iPad Safari real-device behavior** — All tests run in Playwright's simulated browsers. Real iPad Safari rendering of the 9-item scrollable gallery is not tested here.
- **Color palette and child appeal** — Whether the 5 new page themes (Kelp Forest, Treasure Chest, Jellyfish Meadow, Whirlpool Vortex, Starfish Beach) are engaging for a 6-year-old is a subjective assessment outside automated testing.

## Notes for Tester

- The 5 new coloring pages (5-9) will show as blank thumbnails in the gallery until art is generated. This is expected and documented.
- The test count baseline is 103. If it changes, investigate whether new tests were added or existing ones were removed.
- The gallery CSS fix (`max-height: 260px`) is specifically tuned for the Playwright viewport (1280×800). If viewport dimensions change in test config, gallery layout tests may need adjustment.
- `app.js` DOMContentLoaded now only contains hash-routing bootstrap. If adding new initialization, verify E2E tests still pass afterward.
