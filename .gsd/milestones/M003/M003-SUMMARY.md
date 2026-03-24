---
id: M003
title: "Mermaid Art Rework"
status: completed
slices_completed: [S01, S02, S03]
total_tests: 104
test_result: 104 passed, 0 failed
duration: ~2h across 3 slices (8 tasks)
completed_at: 2026-03-23
code_changes: 34 files changed, 377 insertions(+), 235 deletions(-) across frontend, pipeline, and tests
requirement_outcomes:
  - id: DRSU-01
    description: "User sees a single base mermaid (gallery shows one mermaid at a time, swap replaces entire character)"
    from_status: active
    to_status: validated
    proof: "9-mermaid gallery implemented in dressup.js — each character is a complete SVG, swap replaces the entire SVG content. 14 E2E tests in test_dressup.py verify gallery, swap, and recolor behavior."
  - id: DRSU-02
    description: "Hair style variants delivered via 9 diverse characters with distinct hair styles"
    from_status: active
    to_status: validated
    proof: "9 AI-generated mermaid SVGs (mermaid-1.svg through mermaid-9.svg) with distinct hair styles deployed to frontend/assets/svg/dressup/. test_has_nine_characters and test_ids_are_mermaid_1_through_9 confirm."
  - id: DRSU-03
    description: "Eye style variants delivered via 9 diverse characters with distinct eye styles"
    from_status: active
    to_status: validated
    proof: "Same 9 diverse characters each have distinct eye styles. Verified visually in browser and structurally via test suite."
  - id: DRSU-04
    description: "Tail style variants delivered via 9 diverse characters with distinct tail styles"
    from_status: active
    to_status: validated
    proof: "Same 9 diverse characters each have distinct tail styles. Verified visually and structurally."
  - id: DEBT-03
    description: "Region masks redesigned with non-overlapping vertical zones"
    from_status: active
    to_status: validated
    proof: "REGIONS in edit.py: hair y2=290, tail y1=550 (gap of 260px). test_regions_do_not_overlap and test_hair_tail_no_vertical_overlap both pass."
  - id: COLR-01
    description: "Coloring pages feature hair/eyes/tail variety across pages"
    from_status: active
    to_status: validated
    proof: "9 coloring page definitions in prompts.py and coloring.js with distinct hair/eyes/tail per page. test_coloring_page_prompts_have_distinct_styles asserts all 9 IDs and prompts are unique."
  - id: DEBT-01
    description: "Debug overlay removed from app.js"
    from_status: active
    to_status: validated
    proof: "_initDebug function, ?debug=1 activation, and triple-tap wiring removed. grep -q '_initDebug' frontend/js/app.js exits 1."
  - id: DEBT-02
    description: "WebKit sparkle E2E test failures fixed"
    from_status: active
    to_status: validated
    proof: "uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit → 2 passed."
---

# M003: Mermaid Art Rework — Milestone Summary

**Reworked both dress-up and coloring art pipelines: 9-character dress-up gallery with AI-generated kawaii mermaids and CSS hue-rotate recoloring, 9 coloring pages with distinct hair/eyes/tail variety, dead code removed, fetch errors handled, and all 104 tests passing.**

## What Was Delivered

### S01: Dress Up Art Rework
Pivoted from the planned multi-layer part-swapping architecture to a flat 9-character gallery. The gpt-image-1 edit API outputs full characters (not isolated parts), and compositing produced visible seams. The gallery approach delivers better art quality: 9 diverse AI-generated kawaii mermaids (mermaid-1 through mermaid-9), each a complete SVG, swapped by replacing the entire SVG content. Recoloring uses CSS `hue-rotate` on the whole `<svg>` element — works universally across all skin tones including dark-skinned characters. Pipeline retained 4-category non-overlapping region masks (DEBT-03 structurally fixed: hair y2=290 < tail y1=550).

### S02: Coloring Art Rework
Expanded coloring gallery from 4 to 9 pages with distinct hair/eyes/tail per page. Each page has explicit "single enclosed shape with clear black outline" prompt language for hair and tail regions. CSS gallery layout fixed for 9-item grid in Playwright viewport. Debug overlay (`_initDebug`, `?debug=1`, triple-tap) fully removed from app.js. WebKit sparkle test failures confirmed already fixed.

### S03: Cleanup & Stability
Added `resp.ok` guards to all 3 frontend `fetch()` calls — HTTP errors now throw instead of silently injecting HTML as SVG. Removed 4 dead pipeline symbols from edit.py (leftovers from the multi-layer pivot). Traced and deployed all 9 coloring page SVGs to frontend. Added regression test for SVG asset existence. Test suite advanced from 103 to 104.

## Verification Evidence

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Code changes exist | 34 files, +377/-235 lines across frontend/pipeline/tests | ✅ |
| All slices complete | S01 ✅, S02 ✅, S03 ✅ — all `[x]` in roadmap | ✅ |
| All slice summaries exist | S01-SUMMARY.md, S02-SUMMARY.md, S03-SUMMARY.md | ✅ |
| Full test suite | `uv run pytest -q` → 104 passed in 45s | ✅ |
| DRSU-01: Single base mermaid | Gallery shows 1 mermaid, swap replaces entire character | ✅ |
| DRSU-02: Hair style variants | 9 characters with distinct hair styles | ✅ |
| DRSU-03: Eye style variants | 9 characters with distinct eye styles | ✅ |
| DRSU-04: Tail style variants | 9 characters with distinct tail styles | ✅ |
| DEBT-03: Non-overlapping regions | hair y2=290 < tail y1=550, tests pass | ✅ |
| 9 dress-up SVGs deployed | `ls frontend/assets/svg/dressup/mermaid-*.svg | wc -l` → 9 | ✅ |
| 9 coloring SVGs deployed | `ls frontend/assets/svg/coloring/*.svg | wc -l` → 9 | ✅ |
| Fetch error guards | 3 `resp.ok` checks across app.js and dressup.js | ✅ |
| Dead code removed | grep for 4 dead symbols exits 1 | ✅ |
| Debug overlay removed | `grep -q '_initDebug' app.js` exits 1 | ✅ |

## Architecture Decisions

1. **Multi-layer → flat gallery pivot** (S01): gpt-image-1 produces full characters, not isolated parts. Clipping created visible seams. Gallery with 9 diverse full mermaids delivers better quality.
2. **CSS hue-rotate recoloring** (S01): Works universally across all skin tones. Per-part fill manipulation broke on dark-skinned characters.
3. **`>= N` assertion style** (S03, D001): Asset count tests use `>= 9` not `== 9` for forward compatibility.
4. **Fetch error guards inside existing try/catch** (S03): Minimal error surface — throw on `!resp.ok` rather than adding new error handling layers.

## Requirement Status Transitions

| Requirement | From | To | Proof |
|-------------|------|----|-------|
| DRSU-01 | active | validated | 9-mermaid gallery, 14 E2E tests |
| DRSU-02 | active | validated | 9 diverse character SVGs with distinct hair |
| DRSU-03 | active | validated | 9 diverse character SVGs with distinct eyes |
| DRSU-04 | active | validated | 9 diverse character SVGs with distinct tails |
| DEBT-03 | active | validated | hair y2=290 < tail y1=550, 2 region tests pass |
| COLR-01 | active | validated | 9 pages with unique hair/eyes/tail, distinctness test |
| DEBT-01 | active | validated | _initDebug fully removed, grep confirms |
| DEBT-02 | active | validated | WebKit sparkle tests pass, no code change needed |

## Known Limitations

- **COLR-02/COLR-03 remain active** — Prompts request closed outlines for hair/tail regions, and all 9 SVGs are deployed, but actual flood-fill quality on generated art requires visual verification. These are structurally addressed but not fully validated.
- **Pipeline/frontend gap** — Pipeline modules (prompts.py, edit.py, assemble.py) retain multi-layer infrastructure that the frontend doesn't use in gallery mode. Not dead code (serves art generation), but creates a conceptual gap.
- **Pages 5-9 art quality** — These SVGs were traced from AI-generated PNGs. Visual quality depends on the AI model's adherence to prompt instructions.

## Cross-Slice Patterns and Lessons

1. **Architecture pivots happen at generation time, not planning time.** The multi-layer plan looked sound until gpt-image-1 revealed it outputs full characters. Plans should include fallback strategies for AI art generation constraints.
2. **CSS hue-rotate > fill manipulation for diverse art.** Per-path fill manipulation breaks on characters with dark skin tones where the heuristic can't distinguish "skin" from "hair." Whole-element hue-rotate preserves relative relationships universally.
3. **Gallery grid CSS must be tested at target viewport.** The 9-item grid with `aspect-ratio: 3/4` produced 821px-tall items that overlapped in Playwright's 1280×800 viewport, despite looking fine in full browser windows. Always test grid expansions at the E2E viewport size.
4. **Hardcoded count assertions lurk in unexpected test files.** Expanding from 4 to 9 coloring pages broke `test_floodfill_unit.py` which had a hardcoded `== 4`. Grep the full test suite for count literals when expanding arrays.
5. **Dead-code grep must use `--include="*.py"` to exclude `__pycache__`** — bytecode in `.pyc` files produces false positives.

## What the Next Milestone Should Know

- **Test baseline: 104 passed.** Any new tests should produce 105+. Run `uv run pytest -q` to verify.
- **Dress-up uses a flat 9-character gallery** — NOT multi-layer part swapping. Read WORKLOG.md for ground truth.
- **Recoloring is CSS `hue-rotate`** on `<svg>` element. Tests must assert `svg.style.filter` not `path[fill]`.
- **All 9 coloring pages have SVGs** in `frontend/assets/svg/coloring/`. Gallery shows real art for all pages.
- **app.js is clean** — DOMContentLoaded only contains hash-routing bootstrap. New initialization goes there.
- **Pipeline edit.py is minimal** — only `create_region_mask()` and `edit_region()` remain after dead code removal.
- **COLR-02 and COLR-03** still need visual verification of flood-fill quality on generated art.

## Files Changed (key files across all slices)

- `frontend/js/dressup.js` — Character gallery swap + hue-rotate recoloring
- `frontend/js/app.js` — 9-button gallery UI, debug overlay removed, fetch guards added
- `frontend/js/coloring.js` — Expanded to 9 coloring page entries
- `frontend/css/style.css` — Gallery grid layout fixes for 9 items
- `frontend/assets/svg/mermaid.svg` — AI-generated default mermaid
- `frontend/assets/svg/dressup/mermaid-{1-9}.svg` — 9 diverse kawaii mermaids
- `frontend/assets/svg/coloring/page-{1-9}-*.svg` — 9 coloring page SVGs
- `src/mermaids/pipeline/prompts.py` — 4-category variants, 9 coloring page definitions
- `src/mermaids/pipeline/edit.py` — Non-overlapping REGIONS, dead code removed
- `src/mermaids/pipeline/assemble.py` — 5-layer assembly infrastructure
- `src/mermaids/pipeline/generate.py` — Updated docstring
- `tests/test_dressup.py` — 14 E2E tests (gallery, swap, hue-rotate recolor)
- `tests/test_masks.py` — 12 tests (regions, assembly, characters)
- `tests/test_generate.py` — 9-page count + distinctness tests
- `tests/test_coloring.py` — 9-item gallery assertion
- `tests/test_floodfill_unit.py` — Updated count assertion
- `tests/test_trace_coloring.py` — SVG asset existence regression test
