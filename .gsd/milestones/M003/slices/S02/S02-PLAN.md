# S02: Coloring Art Rework

**Goal:** Coloring gallery expanded from 4 to 9 pages with distinct hair/eyes/tail variety per page, debug overlay removed, and all tests passing.
**Demo:** `uv run pytest -q` passes 102+ tests; `COLORING_PAGES` in both `prompts.py` and `coloring.js` have 9 entries with distinct style descriptions; `_initDebug()` and its wiring are gone from `app.js`.

## Must-Haves

- 9 coloring page definitions in `prompts.py` with distinct hair style, eye style, and tail style per page (COLR-01)
- 9 matching entries in `frontend/js/coloring.js` `COLORING_PAGES` array
- Prompts explicitly request closed black outlines for hair and tail regions (COLR-02, COLR-03)
- `test_generate.py` asserts `len(results) == 9` instead of `== 4`
- `test_coloring.py` gallery test asserts `>= 9` thumbnails
- `_initDebug()` function, `?debug=1` activation, and triple-tap wiring removed from `app.js` (DEBT-01)
- DEBT-02 confirmed already fixed (WebKit sparkle tests pass)
- Full test suite passes (102+)

## Verification

- `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` — passes with 9-page assertion
- `uv run pytest tests/test_coloring.py::TestColoringGallery -v` — passes with `>= 9` assertion
- `uv run pytest -q` — 102+ passed
- `grep -c "page-" src/mermaids/pipeline/prompts.py` returns 9 (9 page entries)
- `grep -c "page-" frontend/js/coloring.js` returns 9 (9 page entries)
- `! grep -q "_initDebug" frontend/js/app.js` — debug overlay fully removed

## Observability / Diagnostics

**Runtime inspection surfaces:**
- `grep -c "_initDebug" frontend/js/app.js` → must return 0 (debug overlay absent)
- `grep -c '"page-' src/mermaids/pipeline/prompts.py` → expect 9
- `grep -c '"page-' frontend/js/coloring.js` → expect 9
- `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` → prints per-page prompt details on failure
- `uv run pytest tests/test_coloring.py::TestColoringGallery -v` → E2E gallery thumbnail count

**Failure-path visibility:**
- If pages 5-9 SVG files are missing (`assets/svg/coloring/page-N-*.svg`), the gallery renders blank thumbnails but remains functional; no JS error thrown — visible only as blank `<img>` elements.
- If `_initDebug` is re-introduced, `grep -q "_initDebug" frontend/js/app.js` exits 0 (failure signal).
- E2E failures on WebKit sparkle tests (`tests/test_e2e.py::TestTouchInteraction --browser webkit`) indicate DEBT-02 regression.

**Redaction:** No secrets or PII involved in this slice.

## Integration Closure

- Upstream surfaces consumed: `src/mermaids/pipeline/prompts.py` (COLORING_PAGES list), `frontend/js/coloring.js` (COLORING_PAGES array), `frontend/js/app.js` (_initDebug)
- New wiring introduced in this slice: 5 new coloring page entries wired end-to-end from prompts → frontend gallery
- What remains before the milestone is truly usable end-to-end: S03 cleanup/stability; art generation of 5 new pages requires `uv run python scripts/generate_coloring.py` + `scripts/trace_all.py` with an OpenAI API key (existing 4 pages remain functional)

## Tasks

- [x] **T01: Expand coloring pages to 9 with distinct hair/eyes/tail variety** `est:30m`
  - Why: Delivers COLR-01 (variety), COLR-02 (hair fillability via prompt), COLR-03 (tail fillability via prompt). Currently only 4 generic pages exist.
  - Files: `src/mermaids/pipeline/prompts.py`, `src/mermaids/pipeline/generate.py`, `frontend/js/coloring.js`, `tests/test_generate.py`, `tests/test_coloring.py`
  - Do: Add 5 new entries (page-5 through page-9) to `COLORING_PAGES` in `prompts.py`, each with distinct hair/eyes/tail description and explicit "single enclosed black outline" language for hair and tail regions. Add matching 5 entries to `COLORING_PAGES` in `coloring.js`. Update `test_generate.py` assertion from `== 4` to `== 9` and rename test. Update `test_coloring.py` assertion from `>= 4` to `>= 9`. Update `generate.py` docstring from "4" to match reality. Add a new test in `test_generate.py` asserting each page prompt mentions a distinct hair style.
  - Verify: `uv run pytest tests/test_generate.py tests/test_coloring.py -v`
  - Done when: 9 coloring page definitions in both Python and JS, all with distinct style descriptions; tests assert 9 pages; full suite passes

- [x] **T02: Remove debug overlay and confirm DEBT-02 already fixed** `est:15m`
  - Why: DEBT-01 requires removing the diagnostic debug overlay. DEBT-02 (WebKit sparkle failures) is already resolved — tests pass on both Chromium and WebKit — just needs formal validation.
  - Files: `frontend/js/app.js`
  - Do: Delete the entire `_initDebug()` function (~60 lines, from the `// -- Debug overlay` comment block through the closing brace). Remove the `if (window.location.search.includes("debug=1"))` block in DOMContentLoaded. Remove the triple-tap wiring block (the `homeNavIcon` variable, `tapCount`, `tapTimer`, and the click event listener). Verify no other references to `_initDebug` remain. Run WebKit sparkle tests to confirm DEBT-02 is already fixed.
  - Verify: `! grep -q "_initDebug" frontend/js/app.js && uv run pytest tests/test_e2e.py -v && uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit`
  - Done when: No debug overlay code in app.js; all E2E tests pass on both Chromium and WebKit; full suite passes 102+

## Files Likely Touched

- `src/mermaids/pipeline/prompts.py`
- `src/mermaids/pipeline/generate.py`
- `frontend/js/coloring.js`
- `frontend/js/app.js`
- `tests/test_generate.py`
- `tests/test_coloring.py`
