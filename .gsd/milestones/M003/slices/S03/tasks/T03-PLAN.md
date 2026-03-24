---
estimated_steps: 4
estimated_files: 7
skills_used:
  - test
---

# T03: Trace coloring pages 5-9 and deploy all 9 SVGs to frontend

**Slice:** S03 — Cleanup & Stability
**Milestone:** M003

## Description

The coloring gallery has 9 page definitions but only 4 SVG art files (pages 1-4). Pages 5-9 have PNGs in `assets/generated/png/coloring/` that need to be traced to SVG and deployed to `frontend/assets/svg/coloring/`. This task runs the existing tracing pipeline (`scripts/trace_all.py`), copies the resulting SVGs to the frontend directory, and adds a test asserting all 9 coloring SVG files exist.

This closes COLR-02/COLR-03 at the asset-existence level — the SVGs will be present for the flood-fill coloring UI. Actual closed-outline quality is enforced by prompt language and requires visual verification after AI art generation.

**Key constraints:**
- Coloring pages MUST be traced with `simplify=True` (binary mode). The existing `trace_coloring_pages()` function already uses this correctly.
- The tracing uses vtracer locally — no API key needed. PNGs already exist.
- There is an existing `copy_coloring_pages_to_frontend()` function in `src/mermaids/pipeline/assemble.py` that copies from `assets/generated/svg/coloring/` to `frontend/assets/svg/coloring/`.

## Steps

1. Run `uv run python scripts/trace_all.py` to trace pages 5-9 PNGs. This reads from `assets/generated/png/coloring/` and writes SVGs to `assets/generated/svg/coloring/`. Pages 1-4 will be traced fresh too (their generated SVGs don't exist in the worktree yet, but the frontend already has them). Verify: `ls assets/generated/svg/coloring/*.svg | wc -l` should be 9.

2. Deploy all 9 SVGs to frontend: run `uv run python -c "from mermaids.pipeline.assemble import copy_coloring_pages_to_frontend; copy_coloring_pages_to_frontend()"` — or simply `cp assets/generated/svg/coloring/*.svg frontend/assets/svg/coloring/`. Verify: `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9.

3. Add a test to `tests/test_trace_coloring.py` in a new class `TestColoringSVGAssets`:
   ```python
   class TestColoringSVGAssets:
       """Verify all 9 coloring page SVGs exist in the frontend directory."""

       def test_all_nine_coloring_svgs_exist(self):
           """All 9 coloring page SVGs are deployed to frontend/assets/svg/coloring/."""
           from pathlib import Path
           svg_dir = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "svg" / "coloring"
           svg_files = sorted(svg_dir.glob("page-*.svg"))
           assert len(svg_files) >= 9, f"Expected 9 coloring SVGs, found {len(svg_files)}: {[f.name for f in svg_files]}"
   ```
   Use `>= 9` not `== 9` to be future-proof.

4. Run full test suite: `uv run pytest -q` → should show 104+ passed (103 existing + 1 new test).

## Must-Haves

- [ ] All 9 coloring page SVGs exist in `assets/generated/svg/coloring/`
- [ ] All 9 coloring page SVGs deployed to `frontend/assets/svg/coloring/`
- [ ] New test asserts all 9 SVGs exist at frontend paths
- [ ] Test uses `>= 9` assertion (not hardcoded `== 9`)
- [ ] Full test suite passes at 104+

## Verification

- `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9
- `uv run pytest tests/test_trace_coloring.py -v` → all pass including new test
- `uv run pytest -q` → 104+ passed, 0 failed

## Observability Impact

- Signals added/changed: New `TestColoringSVGAssets::test_all_nine_coloring_svgs_exist` test provides continuous regression detection — if any coloring SVG is accidentally deleted or missing after a pipeline re-run, the test fails with an explicit list of which SVGs are present vs. expected.
- How a future agent inspects this: `ls frontend/assets/svg/coloring/*.svg | wc -l` → instant asset count. `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` → formal test assertion. The test prints actual file names in the failure message for easy diagnosis.
- Failure state exposed: Missing SVGs produce gallery items with blank thumbnails in the UI and a failing test with explicit file list. The `>= 9` assertion is forward-compatible — adding more pages won't break it.

## Inputs

- `assets/generated/png/coloring/page-5-forest.png` — source PNG for tracing
- `assets/generated/png/coloring/page-6-treasure.png` — source PNG for tracing
- `assets/generated/png/coloring/page-7-jellyfish.png` — source PNG for tracing
- `assets/generated/png/coloring/page-8-whirlpool.png` — source PNG for tracing
- `assets/generated/png/coloring/page-9-starfish.png` — source PNG for tracing
- `scripts/trace_all.py` — tracing script to execute
- `src/mermaids/pipeline/assemble.py` — contains `copy_coloring_pages_to_frontend()` for deployment
- `tests/test_trace_coloring.py` — existing test file to add new test class to

## Expected Output

- `assets/generated/svg/coloring/page-5-forest.svg` — new traced SVG
- `assets/generated/svg/coloring/page-6-treasure.svg` — new traced SVG
- `assets/generated/svg/coloring/page-7-jellyfish.svg` — new traced SVG
- `assets/generated/svg/coloring/page-8-whirlpool.svg` — new traced SVG
- `assets/generated/svg/coloring/page-9-starfish.svg` — new traced SVG
- `frontend/assets/svg/coloring/page-5-forest.svg` — deployed to frontend
- `frontend/assets/svg/coloring/page-6-treasure.svg` — deployed to frontend
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — deployed to frontend
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — deployed to frontend
- `frontend/assets/svg/coloring/page-9-starfish.svg` — deployed to frontend
- `tests/test_trace_coloring.py` — modified with new `TestColoringSVGAssets` class
