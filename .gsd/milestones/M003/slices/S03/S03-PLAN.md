# S03: Cleanup & Stability

**Goal:** Fix fetch 404 handling bugs, remove dead pipeline code from the architecture pivot, trace and deploy coloring pages 5-9 SVGs so the gallery has all 9 pages with real art.
**Demo:** All 3 fetch calls have resp.ok guards, dead functions removed from edit.py with 0 grep hits, all 9 coloring SVGs exist in `frontend/assets/svg/coloring/`, full test suite passes at 104+.

## Must-Haves

- All `fetch()` calls in app.js and dressup.js check `resp.ok` before using the response
- Dead functions (`generate_dressup_variants`, `composite_all_combinations`, `generate_base_mermaid`, `_CATEGORY_TO_REGION`) removed from `edit.py`
- All 9 coloring page SVGs traced and deployed to `frontend/assets/svg/coloring/`
- New test asserts all 9 coloring SVGs exist at frontend paths
- Full test suite at 104+ passed (103 baseline + 1 new SVG-existence test)
- COLR-02 and COLR-03 advanced at asset-existence level (SVGs present for flood-fill coloring UI)

## Observability / Diagnostics

**Runtime signals:**
- Frontend fetch failures: browser console shows `Failed to load mermaid SVG: <status>` / `Failed to load coloring page: <status>` / `Failed to load character SVG: <status>` instead of silently injecting HTML. The UI renders the error div rather than broken SVG.
- Dead-code removal: `grep -rn "generate_dressup_variants" src/` returns exit code 1 after T02. If a future import or call reintroduces the symbol, `uv run pytest` fails with `NameError` or `ImportError`.
- SVG asset presence: `ls frontend/assets/svg/coloring/*.svg | wc -l` returns 9. The SVG-existence test in `tests/test_trace_coloring.py` fails immediately if any file is missing.

**Inspection surfaces:**
- `grep -n "resp.ok\|svgResp.ok" frontend/js/app.js frontend/js/dressup.js` — shows all three fetch guard locations
- `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` — exit code 1 confirms dead code is gone
- `uv run pytest tests/test_trace_coloring.py -v` — shows pass/fail per SVG file by name

**Failure visibility:**
- Missing coloring SVGs: gallery thumbnails are blank; SVG-existence test names the missing file
- Re-introduced dead symbol: `uv run pytest` fails at import time with `NameError: name 'DRESSUP_VARIANTS' is not defined`
- Fetch 404 without resp.ok guard: SVG container renders raw HTML text visible as mangled characters in UI

**Redaction constraints:** None — no secrets are logged; all diagnostic output is file paths and HTTP status codes.

## Verification

- `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` → 2
- `grep -c "resp.ok" frontend/js/dressup.js` → 1
- `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` → no output (exit code 1)
- `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9
- `uv run pytest tests/test_trace_coloring.py -v` → all pass including new SVG-existence test
- `uv run pytest -q` → 104+ passed, 0 failed

## Tasks

- [x] **T01: Add resp.ok checks to all fetch calls in app.js and dressup.js** `est:15m`
  - Why: Three fetch() calls silently accept HTTP error responses and inject HTML error pages where SVG is expected, corrupting the UI
  - Files: `frontend/js/app.js`, `frontend/js/dressup.js`
  - Do: Add `if (!resp.ok) throw new Error(...)` after each fetch call. Use existing try/catch blocks — do not add new ones. Do NOT change `?v=14` cache buster query strings.
  - Verify: `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` → 2; `grep -c "resp.ok" frontend/js/dressup.js` → 1; `uv run pytest -q` → 103+ passed
  - Done when: All 3 fetch calls have resp.ok guards, test suite still green

- [x] **T02: Remove dead pipeline functions from edit.py** `est:20m`
  - Why: Architecture pivot left dead functions that reference nonexistent symbols — `generate_dressup_variants()` would crash with NameError if called
  - Files: `src/mermaids/pipeline/edit.py`, `tests/test_masks.py`
  - Do: Delete `generate_dressup_variants()`, `composite_all_combinations()`, `generate_base_mermaid()`, and `_CATEGORY_TO_REGION` from edit.py. Update module docstring. Update stale DRESSUP_VARIANTS comment in test_masks.py line 116.
  - Verify: `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` → no output; `uv run pytest -q` → 103+ passed
  - Done when: Zero grep hits for removed symbols across src/, scripts/, tests/; full test suite green

- [x] **T03: Trace coloring pages 5-9 and deploy all 9 SVGs to frontend** `est:30m`
  - Why: Gallery has 9 page definitions but only 4 SVG art files — pages 5-9 show blank thumbnails. Closes COLR-02/COLR-03 at asset-existence level.
  - Files: `scripts/trace_all.py`, `frontend/assets/svg/coloring/`, `tests/test_trace_coloring.py`
  - Do: Run trace_all.py to trace 9 PNGs to SVG (uses simplify=True for coloring pages — do NOT use simplify=False). Copy SVGs to frontend. Add test asserting `>= 9` coloring SVGs exist at frontend paths.
  - Verify: `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9; `uv run pytest tests/test_trace_coloring.py -v` → all pass; `uv run pytest -q` → 104+ passed
  - Done when: All 9 SVGs in frontend/assets/svg/coloring/, new existence test passes, full suite at 104+

## Files Likely Touched

- `frontend/js/app.js`
- `frontend/js/dressup.js`
- `src/mermaids/pipeline/edit.py`
- `tests/test_masks.py`
- `scripts/trace_all.py`
- `tests/test_trace_coloring.py`
- `frontend/assets/svg/coloring/page-5-forest.svg`
- `frontend/assets/svg/coloring/page-6-treasure.svg`
- `frontend/assets/svg/coloring/page-7-jellyfish.svg`
- `frontend/assets/svg/coloring/page-8-whirlpool.svg`
- `frontend/assets/svg/coloring/page-9-starfish.svg`
- `assets/generated/svg/coloring/` (9 traced SVGs)
