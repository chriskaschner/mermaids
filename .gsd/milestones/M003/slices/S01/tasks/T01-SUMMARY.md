---
id: T01
parent: S01
milestone: M003
provides:
  - DRESSUP_VARIANTS with 4 categories (tails, hair, eyes, accessories) x 3 variants = 12 total
  - REGIONS dict with 4 non-overlapping bounding boxes (DEBT-03 fixed)
  - assemble_mermaid_svg() producing 5-layer stacked use structure
  - VARIANT_IDS list with 12 IDs including eye-1..3
  - BODY_ID constant and body group in assembled SVG defs
requires: []
affects: []
key_files: []
key_decisions: []
patterns_established: []
observability_surfaces: []
drill_down_paths: []
duration: 25min
verification_result: passed
completed_at: 2026-03-12
blocker_discovered: false
---
# T01: 08-dress-up-art-rework 01

**# Phase 8 Plan 01: Art Pipeline Rework Summary**

## What Happened

# Phase 8 Plan 01: Art Pipeline Rework Summary

**4-category isolated-parts pipeline with non-overlapping region masks, eyes category, and 5-layer SVG assembly replacing the former 9-full-character single-use structure**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-12T00:00:00Z
- **Completed:** 2026-03-12
- **Tasks:** 2 (both TDD: RED commit + GREEN commit each)
- **Files modified:** 5

## Accomplishments

- Added eyes category to DRESSUP_VARIANTS (big round, sparkle star-pupil, sleepy half-closed)
- Redesigned REGIONS with 4 non-overlapping vertical zones fixing DEBT-03 (hair y2=290 < tail y1=550)
- Updated generate_dressup_variants() to iterate 4 categories producing 12 variants (not 9)
- Reworked assemble_mermaid_svg() to produce 5 stacked use elements (tail > body > hair > eyes > acc)
- Added BODY_ID constant and body group in defs as static base layer

## Task Commits

Each task committed atomically with TDD RED then GREEN:

1. **Task 1: Update prompts and region masks for 4-category isolated parts**
   - `0825eac` test(08-01): add failing tests for 4-category isolated parts (RED)
   - `f8daf62` feat(08-01): add 4-category isolated parts pipeline (prompts + regions) (GREEN)

2. **Task 2: Rework SVG assembly for multi-layer stacked use elements**
   - `bcb5758` test(08-01): add failing tests for multi-layer SVG assembly (RED)
   - `a144ccf` feat(08-01): rework SVG assembly to 5-layer stacked use structure (GREEN)

## Files Created/Modified

- `src/mermaids/pipeline/prompts.py` - Added eyes category (eye-1..3), updated all variant prompts to specify "isolated part only, keep rest of character unchanged", refined DRESSUP_BASE_PROMPT for neutral base body
- `src/mermaids/pipeline/edit.py` - Redesigned REGIONS with 4 non-overlapping vertical zones, added "eyes" to _CATEGORY_TO_REGION, updated generate_dressup_variants() for 4 categories/12 variants
- `src/mermaids/pipeline/assemble.py` - Added BODY_ID constant, updated VARIANT_IDS to 12, added _LAYERS structure, reworked assemble_mermaid_svg() to accept base_traced_svg and produce 5-layer use structure
- `tests/test_masks.py` - Added TestRegions (4 bboxes, non-overlap, DEBT-03, eyes in face area), TestDressupVariantsPrompts (4 categories, 12 total, eyes), updated TestGenerateDressupVariants to expect 12 variants
- `tests/test_assemble.py` - Updated VARIANT_IDS to 12, added body.svg to fixture, added tests for 5-use-elements, layer stacking, body group in defs, data-category attributes, 13 defs groups; updated copy test to expect 12

## Decisions Made

- **acc region moved to torso/collar zone (y 450-549):** The plan's suggested coordinates for acc (top-of-head area) overlapped with hair. Moving to torso/collar achieves strictly non-overlapping layout without changing the accessory concept (necklace, wand, companion on shoulder are all mid-body items).
- **assemble_mermaid_svg() uses optional keyword-only base_traced_svg parameter:** Keeps backward compatibility (defaults to None, creates empty body group). Callers pass the base body traced SVG path.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Redesigned acc region to resolve overlap with hair**
- **Found during:** Task 1 (REGIONS implementation)
- **Issue:** Plan's suggested acc coordinates (250, 0, 774, 200) overlap with hair region (150, 0, 874, 280) because both have y1=0 and share x range. Test `test_regions_do_not_overlap` failed.
- **Fix:** Moved acc to torso/collar zone (200, 450, 824, 549) -- between eyes (y 300-440) and tail (y 550-1024). Accessories like necklace, bubble wand, and shoulder companions are mid-body items, making this placement physically accurate.
- **Files modified:** src/mermaids/pipeline/edit.py
- **Verification:** All region overlap tests pass; hair y2=290 < tail y1=550 (DEBT-03 verified)
- **Committed in:** f8daf62 (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Required to satisfy the non-overlap constraint the plan specified. Accessory region semantics remain appropriate (mid-body items). No scope creep.

## Diagnostics

- **Region overlap check:** `uv run pytest tests/test_masks.py::TestRegions -v` — 3 tests verify non-overlapping bounding boxes and DEBT-03 hair/tail separation
- **Assembly structure:** `uv run pytest tests/test_assemble.py -v` — 17 tests verify 5-layer use elements, body group in defs, data-category attributes, 13 defs groups
- **REGIONS dict inspection:** `python -c "from mermaids.pipeline.edit import REGIONS; print(REGIONS)"` — shows all 4 bounding boxes
- **VARIANT_IDS inspection:** `python -c "from mermaids.pipeline.assemble import VARIANT_IDS; print(VARIANT_IDS)"` — should list 12 IDs

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_masks.py -v` | 0 | ✅ pass | ~2s |
| 2 | `uv run pytest tests/test_assemble.py -v` | 0 | ✅ pass | ~2s |
| 3 | Region non-overlap assertion (hair y2=290 < tail y1=550) | — | ✅ pass | in-test |
| 4 | 4 categories × 3 variants = 12 total verified | — | ✅ pass | in-test |

## Issues Encountered

None beyond the region overlap issue documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Pipeline modules are ready for Phase 9 (UI rework)
- frontend/js/dressup.js needs updating to use 5 active-{layer} use elements instead of active-character
- The frontend needs a new "eyes" tab added to the category tab bar
- All 33 pipeline unit tests pass (16 mask + 17 assemble)

---
*Phase: 08-dress-up-art-rework*
*Completed: 2026-03-12*
