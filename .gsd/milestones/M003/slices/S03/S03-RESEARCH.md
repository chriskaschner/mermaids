# S03: Cleanup & Stability — Research

**Date:** 2026-03-23

## Summary

S03 is focused cleanup work: fix two specific fetch 404 bugs in frontend JS, remove dead pipeline code left behind from the multi-layer compositing pivot, and trace the 5 missing coloring page SVGs (pages 5-9) so the gallery has real art. The codebase is in excellent shape — 103 tests pass, WebKit sparkle (DEBT-02) is already confirmed resolved, and the generated assets directory is clean with no stale composites or parts. There is no novel technology, no risky integration, and no architectural ambiguity.

The two active requirements (COLR-02, COLR-03) address whether AI-generated coloring pages have closed outlines that flood-fill can color. Prompts were updated in S02 for pages 5-9 with explicit "single enclosed shape with clear black outline" language; the PNGs exist in `assets/generated/png/coloring/` for all 9 pages. S03 should trace those PNGs to SVG, deploy them, and add a test confirming all 9 SVG assets exist at their expected frontend paths.

The dead code situation is clear: `generate_dressup_variants()` in `edit.py` references `DRESSUP_VARIANTS` which no longer exists in `prompts.py` — a latent `NameError` if ever called. `composite_all_combinations()` is also dead. Both can be removed safely — no test imports or calls them directly (tests only mock `edit_region` and `create_region_mask`, which are still live).

## Recommendation

Execute as three tightly scoped tasks:

1. **T01 — Fix fetch 404 handling (app.js + dressup.js):** Add `resp.ok` checks in `renderDressUp()` (app.js line 57), the character SVG overlay fetch (app.js line 223), and `fetchCharacterSVG()` (dressup.js line 51). Each should throw or surface the error UI instead of injecting an HTML error page into the SVG slot. Add a test that mocks a 404 response and asserts the error div renders.

2. **T02 — Remove dead pipeline code (edit.py):** Delete `generate_dressup_variants()`, `composite_all_combinations()`, and `generate_base_mermaid()` from `edit.py`. The remaining live functions (`create_region_mask`, `edit_region`) and constants (`REGIONS`, `DRESSUP_BASE_PROMPT`) are still tested and needed. Update `test_masks.py` comment on line 116 which mentions `DRESSUP_VARIANTS` to avoid confusion. Verify `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid" scripts/` — if scripts reference these, update them too.

3. **T03 — Trace and deploy coloring pages 5-9:** Run `uv run python scripts/trace_all.py` logic (or inline it) to trace the 5 existing PNGs (`page-5-forest.png` through `page-9-starfish.png`) and copy the resulting SVGs to `frontend/assets/svg/coloring/`. Add a test asserting all 9 coloring SVG files exist at `frontend/assets/svg/coloring/page-{N}-*.svg`. This validates COLR-02/COLR-03 at the asset-existence level (actual closed-outline quality requires visual verification after AI art generation, which is already noted in requirements as prompt-level enforcement).

## Implementation Landscape

### Key Files

- `frontend/js/app.js` — Two fetch calls need `resp.ok` checks: line 57 (`fetch("assets/svg/mermaid.svg")`) and line 223 (`fetch(page.file)` for the SVG overlay in `renderColoringPage()`). The try/catch pattern already exists — add `if (!resp.ok) throw new Error(...)` after each fetch.
- `frontend/js/dressup.js` — `fetchCharacterSVG()` at line 51 has a `fetch()` call with no `resp.ok` check. Same fix: add a check before `resp.text()`.
- `src/mermaids/pipeline/edit.py` — Contains dead functions: `generate_dressup_variants()` (line ~170, references nonexistent `DRESSUP_VARIANTS`), `composite_all_combinations()` (line ~218, ~100 lines), and `generate_base_mermaid()` (line ~157, only called by the dead `generate_dressup_variants`). Live functions to keep: `create_region_mask()`, `edit_region()`, `REGIONS`, `_CATEGORY_TO_REGION`, `DRESSUP_BASE_PROMPT` import.
- `tests/test_masks.py` — Line 116 comment says "Character prompt tests (replaces DRESSUP_VARIANTS tests)" — update comment. No test calls removed functions directly, only `edit_region` and `create_region_mask`.
- `scripts/generate_dressup.py` — Check if it references removed functions; update or remove stale calls.
- `assets/generated/png/coloring/` — Contains all 9 PNGs already (pages 1-9). Pages 5-9 just need tracing to SVG.
- `frontend/assets/svg/coloring/` — Currently has only 4 SVGs (pages 1-4). Pages 5-9 SVGs must be added here.
- `scripts/trace_all.py` — Has `trace_coloring_pages()` which does exactly what T03 needs. T03 can invoke this script to trace pages 5-9.

### Build Order

1. **T01 first** — Fetch error handling is a self-contained JS bug fix with clear test pattern. Unblocks any future test that mocks 404 responses.
2. **T02 second** — Dead code removal is independent of T01 but clarifies the codebase before final pass. Verify test suite still green after removal.
3. **T03 last** — Tracing SVGs requires the pipeline to be clean and tests to be green. A new assertion test for all-9-SVGs-exist closes COLR-02/COLR-03 at the testable level.

### Verification Approach

```bash
# After T01: fetch error test passes
uv run pytest tests/test_e2e.py -v -k "error" --browser chromium

# After T02: removed functions gone, tests still green
grep -rn "composite_all_combinations\|generate_dressup_variants\|generate_base_mermaid" src/ scripts/ tests/
# → must return nothing
uv run pytest -q  # → 103+ passed

# After T03: all 9 coloring SVGs exist
ls frontend/assets/svg/coloring/ | wc -l  # → 9
uv run pytest -q  # → all pass including new SVG-existence test

# Full baseline confirmation
uv run pytest tests/test_e2e.py -v --browser webkit  # DEBT-02 still resolved
```

## Constraints

- **DEBT-02 is already resolved** — S03-CONTEXT.md mentions "Fix WebKit sparkle failures (DEBT-02)" but the S02 summary and REQUIREMENTS.md both confirm DEBT-02 is validated: `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit` → 2 passed. Do not reopen this work item. The S03 context was authored before S02 completed.
- **Dead code has a latent NameError** — `generate_dressup_variants()` in `edit.py` references `DRESSUP_VARIANTS` which doesn't exist in `prompts.py`. This would crash if called. Removing the function entirely is the correct fix — not patching the reference.
- **Asset generation requires API key** — Tracing (T03) uses vtracer locally (no API needed). The PNGs already exist. Only if new art were needed would an API key be required.
- **Test baseline is 103 passing** — Any change that drops the count or introduces failures is a regression.
- **Cache buster version in imports is `?v=14`** — If any JS file changes, the version query string in import statements (`import ... from "./foo.js?v=14"`) must NOT be changed unless module exports change. These are cache busters, not version assertions.

## Common Pitfalls

- **Removing `generate_base_mermaid()` from edit.py** — `generate_base_mermaid()` is only called by `generate_dressup_variants()`. Confirm with `grep -rn "generate_base_mermaid" scripts/` before removing. The worklog says `scripts/generate_dressup.py` was updated to use `generate_dressup_characters()` — verify it doesn't reference the old function.
- **Tracing with `simplify=True` vs `simplify=False`** — Coloring pages must use `simplify=True` (binary mode) per the existing `trace_coloring_pages()` implementation and `test_trace_coloring_page_uses_simplify_true` test. Dress-up characters use `simplify=False`. Do not mix them.
- **Counting test assertions** — `test_floodfill_unit.py` was burned by a hardcoded `== 4` in S02. When adding the all-9-SVGs test, do not use `== 4` — use `== 9` or `>= 9`.
- **resp.ok check placement** — `fetch()` in app.js is already inside a try/catch. The `resp.ok` check should throw inside that try block so the catch handles it and renders the error div. Don't add a second try/catch.
- **`_CATEGORY_TO_REGION` in edit.py** — This dict is only used by `generate_dressup_variants()`. Once that function is removed, `_CATEGORY_TO_REGION` is dead too. Remove it together.

## Open Risks

- **pages 5-9 SVG visual quality** — vtracer in binary/simplify mode on these AI-generated B&W coloring pages may not produce perfectly closed shapes, especially for hair and tail regions. The test will assert file existence (testable) but closed-outline quality (COLR-02/COLR-03) still requires visual inspection. This risk exists regardless of S03 — it's inherent to AI art generation.
- **scripts/generate_dressup.py references** — If this script still imports `generate_dressup_variants`, removing it from `edit.py` will break the script. Check before removing.
