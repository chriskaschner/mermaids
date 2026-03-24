# S03: Cleanup & Stability — UAT Script

## Preconditions
- Working directory: project root (mermaids repo)
- Python environment: `uv` configured with project dependencies
- All S03 tasks (T01, T02, T03) completed
- No uncommitted changes outside S03 scope

---

## Test Case 1: Fetch Error Guards — app.js mermaid SVG fetch

**What it verifies:** renderDressUp() throws on HTTP error instead of injecting HTML as SVG

**Steps:**
1. Run `grep -n "resp.ok" frontend/js/app.js`
2. Confirm line ~58 contains: `if (!resp.ok) throw new Error(\`Failed to load mermaid SVG: ${resp.status}\`);`
3. Confirm the throw is INSIDE the existing try block (lines 56–108), not in a new try/catch

**Expected:** Guard exists, error message includes status code, throw is inside existing error handling

---

## Test Case 2: Fetch Error Guards — app.js coloring page fetch

**What it verifies:** renderColoringPage() throws on HTTP error for coloring page assets

**Steps:**
1. Run `grep -n "svgResp.ok" frontend/js/app.js`
2. Confirm line ~225 contains: `if (!svgResp.ok) throw new Error(\`Failed to load coloring page: ${svgResp.status}\`);`
3. Confirm the throw is INSIDE the existing try block (lines 152–304)

**Expected:** Guard exists on the `svgResp` variable (not `resp`), error message mentions "coloring page"

---

## Test Case 3: Fetch Error Guards — dressup.js character SVG fetch

**What it verifies:** fetchCharacterSVG() throws on HTTP error for dress-up character SVGs

**Steps:**
1. Run `grep -n "resp.ok" frontend/js/dressup.js`
2. Confirm line ~52 contains: `if (!resp.ok) throw new Error(\`Failed to load character SVG: ${resp.status}\`);`
3. Verify that the error propagates to the caller in app.js (which has its own try/catch)

**Expected:** Guard exists, no new try/catch was added in dressup.js

---

## Test Case 4: Fetch guards — total count

**What it verifies:** Exactly 3 fetch guards exist across both files (no more, no fewer)

**Steps:**
1. Run `grep -c "resp.ok\|svgResp.ok" frontend/js/app.js` → expect 2
2. Run `grep -c "resp.ok" frontend/js/dressup.js` → expect 1

**Expected:** 2 + 1 = 3 total guards

---

## Test Case 5: Cache busters preserved

**What it verifies:** T01 did not modify existing `?v=14` query strings

**Steps:**
1. Run `grep -c "?v=14" frontend/js/app.js frontend/js/dressup.js`
2. Expect app.js: 3, dressup.js: 1

**Expected:** 4 total `?v=14` references unchanged

---

## Test Case 6: Dead code — generate_dressup_variants removed

**What it verifies:** The function that would crash with NameError is gone from the entire codebase

**Steps:**
1. Run `grep --include="*.py" -rn "generate_dressup_variants" src/ scripts/ tests/`
2. Expect exit code 1 (no matches)

**Expected:** Zero hits in any Python source file

---

## Test Case 7: Dead code — all four symbols removed

**What it verifies:** _CATEGORY_TO_REGION, composite_all_combinations, generate_base_mermaid also removed

**Steps:**
1. Run `grep --include="*.py" -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/`
2. Expect exit code 1

**Expected:** Zero hits for any of the four removed symbols

---

## Test Case 8: Dead code — orphaned imports cleaned

**What it verifies:** Imports only used by deleted functions were also removed

**Steps:**
1. Run `grep -n "generate_image\|GENERATED_PNG_DIR\|RETRY_BASE_DELAY\|RETRY_MAX" src/mermaids/pipeline/edit.py`
2. Expect exit code 1 (no matches)
3. Run `python -c "import mermaids.pipeline.edit"` → should succeed with no warnings

**Expected:** No orphaned imports remain in edit.py

---

## Test Case 9: Dead code — edit.py module docstring updated

**What it verifies:** Module docstring describes only remaining functions

**Steps:**
1. Run `head -10 src/mermaids/pipeline/edit.py`
2. Confirm docstring mentions `create_region_mask` and `edit_region`
3. Confirm docstring does NOT mention `generate_dressup_variants` or variant generation

**Expected:** Docstring reflects the trimmed module

---

## Test Case 10: Dead code — test comment updated

**What it verifies:** Stale DRESSUP_VARIANTS reference removed from test_masks.py

**Steps:**
1. Run `grep -n "DRESSUP_VARIANTS" tests/test_masks.py`
2. Expect exit code 1

**Expected:** No references to the removed symbol in test comments

---

## Test Case 11: Coloring SVGs — all 9 exist at frontend path

**What it verifies:** Pages 1-9 are all deployed to frontend/assets/svg/coloring/

**Steps:**
1. Run `ls frontend/assets/svg/coloring/*.svg | sort`
2. Confirm exactly 9 files: page-1-underwater.svg through page-9-starfish.svg

**Expected:** 9 SVG files, all with `page-N-name.svg` naming pattern

---

## Test Case 12: Coloring SVGs — pages 5-9 are new additions

**What it verifies:** The 5 previously-missing SVGs now exist

**Steps:**
1. Run `ls -la frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg`
2. Confirm: page-5-forest.svg, page-6-treasure.svg, page-7-jellyfish.svg, page-8-whirlpool.svg, page-9-starfish.svg

**Expected:** All 5 files exist with non-zero size

---

## Test Case 13: Coloring SVGs — valid SVG content

**What it verifies:** Deployed SVGs contain actual SVG markup (not empty or corrupted)

**Steps:**
1. Run `head -1 frontend/assets/svg/coloring/page-5-forest.svg`
2. Confirm output starts with `<svg` or `<?xml`
3. Repeat for page-9-starfish.svg

**Expected:** Valid SVG opening tags

---

## Test Case 14: SVG existence test — regression coverage

**What it verifies:** TestColoringSVGAssets test exists and uses forward-compatible assertion

**Steps:**
1. Run `grep -A5 "test_all_nine_coloring_svgs_exist" tests/test_trace_coloring.py`
2. Confirm assertion uses `>= 9` (not `== 9`)
3. Run `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v`

**Expected:** Test passes, uses >= 9 assertion

---

## Test Case 15: Full test suite — green at 104+

**What it verifies:** No regressions from S03 changes, test count advanced from 103 baseline

**Steps:**
1. Run `uv run pytest -q`
2. Confirm output shows `104 passed`
3. Confirm `0 failed`

**Expected:** 104 passed, 0 failed

---

## Edge Cases

### Edge Case A: Fetch guard does NOT create new error handling paths
Verify that no new `try { }` or `catch { }` blocks were added in app.js or dressup.js by T01 — the throws should land in pre-existing catch blocks.

### Edge Case B: __pycache__ bytecode contains stale symbols
`grep -rn "generate_dressup_variants" src/` (without `--include="*.py"`) may match `.pyc` files. This is expected stale bytecode and is regenerated on next import. Always use `--include="*.py"` for source verification.

### Edge Case C: trace_all.py is safe to re-run
Run `uv run python scripts/trace_all.py` — it should skip existing SVGs without error. No files should be overwritten or deleted.
