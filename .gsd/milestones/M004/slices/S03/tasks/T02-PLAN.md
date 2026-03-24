---
estimated_steps: 3
estimated_files: 2
skills_used:
  - test
  - agent-browser
---

# T02: Run full test suite and verify gallery renders all 9 thumbnails

**Slice:** S03 — Coloring Page Art Fix
**Milestone:** M004

## Description

Validates the complete fix end-to-end: runs the full non-E2E test suite to confirm 116+ tests pass (including the new content-quality test from T01), then uses a browser to verify all 9 coloring gallery thumbnails render visible art. This proves COLR-04 is satisfied.

## Steps

1. **Run the full non-E2E test suite:**
   ```bash
   uv run pytest tests/ -x --ignore=tests/test_e2e.py --ignore=tests/test_coloring.py --ignore=tests/test_dressup.py -q
   ```
   Confirm 116+ tests pass. The ignored test files are Playwright E2E tests that need a running server — the pipeline/asset tests in `test_trace_coloring.py` are sufficient to prove the SVG content.

2. **Start the dev server and verify gallery rendering:**
   - Start the app server (e.g. `python -m http.server 8080 --directory frontend` or the project's dev server)
   - Navigate to `http://localhost:8080/#/coloring` in the browser
   - Verify all 9 gallery thumbnail tiles are visible — none should be blank white rectangles
   - Click on a page-5+ thumbnail (e.g. "Kelp Forest") and verify the coloring canvas loads with visible black-outline line art

3. **Confirm test count meets milestone requirement:**
   - Total test count should be ≥116 (115 existing + 1 new content-quality test)
   - This exceeds the M004 milestone requirement of 104+ tests

## Must-Haves

- [ ] Full non-E2E test suite passes with 116+ tests
- [ ] All 9 coloring gallery thumbnails render visible art in the browser
- [ ] At least one page-5+ coloring page loads on the canvas with visible line art

## Verification

- `uv run pytest tests/ -x --ignore=tests/test_e2e.py --ignore=tests/test_coloring.py --ignore=tests/test_dressup.py -q` — 116+ passed, 0 failed
- Browser shows 9 non-blank gallery thumbnails at `#/coloring`

## Inputs

- `tests/test_trace_coloring.py` — contains the new content-quality test from T01
- `frontend/assets/svg/coloring/page-5-forest.svg` — placeholder SVG from T01
- `frontend/assets/svg/coloring/page-6-treasure.svg` — placeholder SVG from T01
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — placeholder SVG from T01
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — placeholder SVG from T01
- `frontend/assets/svg/coloring/page-9-starfish.svg` — placeholder SVG from T01

## Expected Output

- `tests/test_trace_coloring.py` — all tests pass (no modifications needed, just execution)
- `frontend/assets/svg/coloring/page-5-forest.svg` — confirmed rendering in browser (no modifications needed)
