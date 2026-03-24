# S03: Coloring Page Art Fix

**Goal:** All 9 coloring gallery pages show real mermaid art (pages 5-9 no longer blank).
**Demo:** Open `#/coloring` in the app — all 9 gallery thumbnails render visible mermaid artwork. Clicking any thumbnail loads a coloring page with actual line art.

## Must-Haves

- Pages 5-9 coloring SVGs (`page-5-forest.svg` through `page-9-starfish.svg`) contain real multi-path mermaid art (≥5 `<path` elements each), not 170-byte vtracer stubs
- Content-quality test asserts all 9 SVGs have ≥5 paths — fails on stubs, passes on real art
- All existing tests continue to pass (116+ total)

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && uv run pytest tests/test_trace_coloring.py -v` — all tests pass including the new `test_all_coloring_svgs_have_real_art`
- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && uv run pytest tests/ -x --ignore=tests/test_e2e.py --ignore=tests/test_coloring.py --ignore=tests/test_dressup.py -q` — all non-E2E tests pass
- `for f in frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg; do count=$(grep -c '<path' "$f"); test "$count" -ge 5 || echo "FAIL: $f has $count paths"; done` — no FAIL output

## Tasks

- [x] **T01: Write content-quality test and generate placeholder coloring SVGs for pages 5-9** `est:45m`
  - Why: Pages 5-9 are 170-byte empty vtracer stubs. No API key is available to run the AI pipeline, so we create scene-themed geometric placeholder SVGs (same pattern as `generate_dressup_outlines.py --placeholder`). A content-quality test locks the invariant that all 9 SVGs have real art.
  - Files: `tests/test_trace_coloring.py`, `scripts/generate_coloring_placeholders.py`, `frontend/assets/svg/coloring/page-{5..9}-*.svg`
  - Do: (1) Add `test_all_coloring_svgs_have_real_art` to `TestColoringSVGAssets` in `tests/test_trace_coloring.py` — asserts every `page-*.svg` in `frontend/assets/svg/coloring/` has ≥5 `<path` elements. (2) Create `scripts/generate_coloring_placeholders.py` that builds 5 scene-themed 1024x1024 B&W outline SVGs — each with unique mermaid + scene elements (forest/kelp, treasure chest, jellyfish, whirlpool, starfish beach) using the same geometric placeholder pattern as `generate_dressup_outlines.py`. Each SVG must have ≥8 `<path` elements. (3) Run the script to generate the SVGs. (4) Copy them to `frontend/assets/svg/coloring/` replacing the stubs. (5) Verify new test passes.
  - Verify: `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` — both asset tests pass
  - Done when: All 9 coloring SVGs in `frontend/assets/svg/coloring/` have ≥5 `<path` elements and the new test passes

- [x] **T02: Run full test suite and verify gallery renders all 9 thumbnails** `est:20m`
  - Why: Proves the replacement SVGs don't break anything and all 9 gallery thumbnails render in the browser. Validates COLR-04 end-to-end.
  - Files: `tests/test_trace_coloring.py`, `frontend/assets/svg/coloring/page-*.svg`
  - Do: (1) Run the full non-E2E test suite to confirm 116+ tests pass. (2) Start the dev server and use Playwright/browser to navigate to `#/coloring` and verify all 9 gallery thumbnails are visible and non-blank. (3) Click a page-5+ thumbnail and verify the coloring canvas loads with visible line art.
  - Verify: `uv run pytest tests/ -x --ignore=tests/test_e2e.py --ignore=tests/test_coloring.py --ignore=tests/test_dressup.py -q` passes, plus browser verification of gallery
  - Done when: 116+ tests pass and all 9 gallery thumbnails render visible mermaid art in the browser

## Observability / Diagnostics

**Runtime signals:**
- `scripts/generate_coloring_placeholders.py` prints each output file's name, size in bytes, and `<path` count to stdout. On write failure it prints `ERROR: failed to write <path>: <reason>` to stderr and exits non-zero.
- The content-quality test (`test_all_coloring_svgs_have_real_art`) reports every failing SVG name + path count in the assertion message, giving immediate visibility into which files are stubs.

**Inspection surfaces:**
- `for f in frontend/assets/svg/coloring/page-*.svg; do echo "$f: $(grep -c '<path' "$f") paths, $(wc -c < "$f")B"; done` — one-liner to audit all 9 files at any time.
- `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` — authoritative pass/fail gate for art quality.

**Failure state:**
- If a stub is accidentally re-deployed (170-byte vtracer empty), `test_all_coloring_svgs_have_real_art` fails with the specific filename and "0 paths" in the assertion error. The gallery thumbnail for that page will be blank white.
- If the script fails to write a file, it exits non-zero and prints the OS error to stderr, leaving the stub in place so the test catches it.

**Redaction:** No secrets or PII involved; all signals are safe to log.

## Files Likely Touched

- `tests/test_trace_coloring.py`
- `scripts/generate_coloring_placeholders.py`
- `frontend/assets/svg/coloring/page-5-forest.svg`
- `frontend/assets/svg/coloring/page-6-treasure.svg`
- `frontend/assets/svg/coloring/page-7-jellyfish.svg`
- `frontend/assets/svg/coloring/page-8-whirlpool.svg`
- `frontend/assets/svg/coloring/page-9-starfish.svg`
