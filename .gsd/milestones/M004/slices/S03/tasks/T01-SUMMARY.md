---
id: T01
parent: S03
milestone: M004
provides:
  - content-quality test asserting all 9 coloring SVGs have ≥5 paths
  - scripts/generate_coloring_placeholders.py for scene-themed placeholder SVGs
  - 5 real placeholder SVGs replacing 170-byte vtracer stubs (pages 5-9)
key_files:
  - tests/test_trace_coloring.py
  - scripts/generate_coloring_placeholders.py
  - frontend/assets/svg/coloring/page-5-forest.svg
  - frontend/assets/svg/coloring/page-6-treasure.svg
  - frontend/assets/svg/coloring/page-7-jellyfish.svg
  - frontend/assets/svg/coloring/page-8-whirlpool.svg
  - frontend/assets/svg/coloring/page-9-starfish.svg
key_decisions:
  - Used textwrap.dedent + f-strings (same pattern as generate_dressup_outlines.py) for inline SVG generation — no external dependencies needed
  - Stub-detection threshold set at 500 bytes so re-running the script auto-replaces stubs but skips real art
  - Each scene SVG reuses a shared _MERMAID_BODY template (15 path-producing elements) plus 5+ scene-specific elements — floor for path count is 18+, well above ≥8 requirement
patterns_established:
  - Placeholder SVG generation pattern: shared body template + per-scene element dict + f-string composition → write to output_dir
  - Content-quality test pattern: glob page-*.svg, count "<path" occurrences, assert all ≥ threshold
observability_surfaces:
  - scripts/generate_coloring_placeholders.py prints filename, size, path count per SVG to stdout; ERROR to stderr on write failure
  - test_all_coloring_svgs_have_real_art reports each failing SVG name + path count in assertion message
  - Audit command: for f in frontend/assets/svg/coloring/page-*.svg; do echo "$f: $(grep -c '<path' "$f") paths"; done
duration: ~20m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T01: Write content-quality test and generate placeholder coloring SVGs for pages 5-9

**Replaced 5 empty 170-byte vtracer stubs with 1024×1024 scene-themed mermaid placeholder SVGs (18–28 paths each) and added a content-quality pytest that fails on stubs and passes on real art.**

## What Happened

The five coloring SVGs for pages 5-9 were 170-byte vtracer empty stubs (`width="1" height="1"`, zero `<path` elements). With no OpenAI API key available, the plan called for scene-themed geometric placeholder SVGs using the same B&W outline pattern as `generate_dressup_outlines.py --placeholder`.

1. **Added `test_all_coloring_svgs_have_real_art`** to the existing `TestColoringSVGAssets` class in `tests/test_trace_coloring.py`. The test globs `page-*.svg`, counts `<path` occurrences, and fails with a list of `filename: N paths` for any SVG below 5. Confirmed it failed on the stubs before implementing the fix.

2. **Created `scripts/generate_coloring_placeholders.py`** with:
   - A shared `_MERMAID_BODY` template string (head, eyes, hair, torso, tail, fins, arms, hands — 15 `<path`/`<ellipse`/`<circle` elements)
   - Per-scene element dicts for 5 scenes: forest (kelp stalks + bubbles + ocean floor), treasure (chest + coins + gems + floor), jellyfish (3 jellyfish bells + tentacles), whirlpool (3 vortex rings + swirl detail + bubbles), starfish (2 starfish + 2 sand dollars + shell + sandy floor)
   - Auto-detects stubs by file size (< 500 bytes) so re-running is safe
   - Diagnostic output: filename, size in bytes, `<path` count, `✅`/`❌` indicator per file

3. **Ran the script** — all 5 stubs replaced successfully in one pass.

## Verification

- Confirmed new test FAILS on stubs before generation (pages 5-9: 0 paths each).
- Ran `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` → both `test_all_nine_coloring_svgs_exist` and `test_all_coloring_svgs_have_real_art` pass.
- Ran full `test_trace_coloring.py` (6 tests) — all pass.
- Ran broader non-E2E suite (70 tests) — all pass.
- Path check: `for f in frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg; do count=$(grep -c '<path' "$f"); test "$count" -ge 5 || echo "FAIL: $f has $count paths"; done` — no FAIL output.
- XML validity: parsed all 5 SVGs with `xml.etree.ElementTree` — valid XML, correct `viewBox="0 0 1024 1024"`.

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` | 0 | ✅ pass | 0.08s |
| 2 | `uv run pytest tests/test_trace_coloring.py -v` | 0 | ✅ pass (6/6) | 0.12s |
| 3 | `uv run pytest tests/ -x --ignore=tests/test_e2e.py --ignore=tests/test_coloring.py --ignore=tests/test_dressup.py -q` | 0 | ✅ pass (70/70) | 11.99s |
| 4 | `for f in frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg; do count=$(grep -c '<path' "$f"); test "$count" -ge 5 \|\| echo "FAIL: ..."; done` | 0 | ✅ no FAIL output | <1s |
| 5 | `uv run python scripts/generate_coloring_placeholders.py` (content summary) | 0 | ✅ all 5 ≥5 paths | <1s |

## Diagnostics

- **Audit all 9 SVGs:** `for f in frontend/assets/svg/coloring/page-*.svg; do echo "$f: $(grep -c '<path' "$f") paths, $(wc -c < "$f")B"; done`
- **Test failure shape:** `test_all_coloring_svgs_have_real_art` assertion error names every failing SVG with its path count — e.g. `['page-5-forest.svg: 0 paths']`.
- **Regenerate:** `uv run python scripts/generate_coloring_placeholders.py` (idempotent for non-stubs; replace stubs automatically). Add `--force` to overwrite everything.
- **File sizes generated:** page-5 4,393B, page-6 4,465B, page-7 5,294B, page-8 4,663B, page-9 5,081B.

## Deviations

None. Task executed exactly as planned.

## Known Issues

None. The placeholder SVGs are geometric outlines, not AI-generated art. The S03 slice goal (all 9 thumbnails render visible artwork) is met. If AI-generated coloring pages are desired in future, the pipeline in `scripts/trace_all.py` + `generate_dressup_outlines.py` pattern provides the template.

## Files Created/Modified

- `tests/test_trace_coloring.py` — added `test_all_coloring_svgs_have_real_art` to `TestColoringSVGAssets` class
- `scripts/generate_coloring_placeholders.py` — new script generating 5 scene-themed B&W coloring SVGs
- `frontend/assets/svg/coloring/page-5-forest.svg` — replaced 170B stub; 4,393B, 20 paths
- `frontend/assets/svg/coloring/page-6-treasure.svg` — replaced 170B stub; 4,465B, 18 paths
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — replaced 170B stub; 5,294B, 28 paths
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — replaced 170B stub; 4,663B, 18 paths
- `frontend/assets/svg/coloring/page-9-starfish.svg` — replaced 170B stub; 5,081B, 23 paths
- `.gsd/milestones/M004/slices/S03/S03-PLAN.md` — added Observability/Diagnostics section, marked T01 done
