---
id: T03
parent: S03
milestone: M003
provides:
  - All 9 coloring page SVGs traced from PNG and deployed to frontend/assets/svg/coloring/
  - New TestColoringSVGAssets::test_all_nine_coloring_svgs_exist test provides continuous regression detection
key_files:
  - frontend/assets/svg/coloring/page-5-forest.svg
  - frontend/assets/svg/coloring/page-6-treasure.svg
  - frontend/assets/svg/coloring/page-7-jellyfish.svg
  - frontend/assets/svg/coloring/page-8-whirlpool.svg
  - frontend/assets/svg/coloring/page-9-starfish.svg
  - tests/test_trace_coloring.py
  - assets/generated/svg/coloring/
key_decisions:
  - Used direct cp instead of copy_coloring_pages_to_frontend() since both approaches are equivalent and cp is simpler with no side effects
patterns_established:
  - Add >= N (not == N) assertions for asset-count tests to remain forward-compatible when more pages are added
observability_surfaces:
  - "ls frontend/assets/svg/coloring/*.svg | wc -l → 9 (instant asset count)"
  - "uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v → formal test assertion with file list on failure"
  - "test_all_nine_coloring_svgs_exist prints actual file names in assertion failure message for easy diagnosis"
duration: ~5m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T03: Trace coloring pages 5-9 and deploy all 9 SVGs to frontend

**Ran trace_all.py to trace all 9 coloring PNGs to SVG, deployed to frontend/assets/svg/coloring/, and added TestColoringSVGAssets test — full suite at 104 passed.**

## What Happened

All 9 coloring page PNGs in `assets/generated/png/coloring/` were traced to SVG via `uv run python scripts/trace_all.py`, which uses `simplify=True` (binary mode) as required for coloring pages. The script also traced 9 dress-up character PNGs (color mode) as a side effect, producing 18 total SVGs.

The 9 coloring SVGs were then copied directly to `frontend/assets/svg/coloring/` with `cp`, overwriting the 4 existing files (pages 1-4) with freshly-traced versions and adding pages 5-9.

A new `TestColoringSVGAssets` class was added to `tests/test_trace_coloring.py` with `test_all_nine_coloring_svgs_exist`, which asserts `>= 9` page-*.svg files exist at the frontend path. The test is forward-compatible and prints actual file names in its assertion message for easy diagnosis.

## Verification

- `ls assets/generated/svg/coloring/*.svg | wc -l` → 9 ✅
- `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9 ✅
- `uv run pytest tests/test_trace_coloring.py -v` → 5 passed (including new test) ✅
- `uv run pytest -q` → 104 passed, 0 failed ✅
- All slice-level verification checks passed (see table below)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` | 0 (output: 2) | ✅ pass | <1s |
| 2 | `grep -c "resp.ok" frontend/js/dressup.js` | 0 (output: 1) | ✅ pass | <1s |
| 3 | `grep -rn "generate_dressup_variants\|..." src/ scripts/ tests/` | 1 (no output) | ✅ pass | <1s |
| 4 | `ls frontend/assets/svg/coloring/*.svg \| wc -l` | 0 (output: 9) | ✅ pass | <1s |
| 5 | `uv run pytest tests/test_trace_coloring.py -v` | 0 | ✅ pass (5/5) | 1.7s |
| 6 | `uv run pytest -q` | 0 | ✅ pass (104 passed) | 43.6s |

## Diagnostics

- **Asset count:** `ls frontend/assets/svg/coloring/*.svg | wc -l` → instant check; returns 9
- **Test regression:** `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` → fails with explicit file list if any SVG is missing
- **Re-trace:** `uv run python scripts/trace_all.py` → skips existing SVGs; safe to re-run after adding new pages
- **Failure shape:** Missing SVGs show blank gallery thumbnails in UI; test message says `Expected 9 coloring SVGs, found N: [list of names]`

## Deviations

Used `cp assets/generated/svg/coloring/*.svg frontend/assets/svg/coloring/` instead of `copy_coloring_pages_to_frontend()` — functionally identical, simpler invocation. The function itself was not changed.

## Known Issues

None.

## Files Created/Modified

- `assets/generated/svg/coloring/page-{1-9}-*.svg` — 9 newly traced SVGs (generated artifacts)
- `frontend/assets/svg/coloring/page-5-forest.svg` — new coloring page deployed to frontend
- `frontend/assets/svg/coloring/page-6-treasure.svg` — new coloring page deployed to frontend
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — new coloring page deployed to frontend
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — new coloring page deployed to frontend
- `frontend/assets/svg/coloring/page-9-starfish.svg` — new coloring page deployed to frontend
- `frontend/assets/svg/coloring/page-{1-4}-*.svg` — re-deployed (freshly traced, same content)
- `tests/test_trace_coloring.py` — added TestColoringSVGAssets class with test_all_nine_coloring_svgs_exist
