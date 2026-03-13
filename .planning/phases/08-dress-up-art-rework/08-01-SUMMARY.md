---
phase: 08-dress-up-art-rework
plan: 01
subsystem: pipeline
tags: [openai, gpt-image-1, svg, vtracer, python, pillow]

requires: []
provides:
  - DRESSUP_VARIANTS with 4 categories (tails, hair, eyes, accessories) x 3 variants = 12 total
  - REGIONS dict with 4 non-overlapping bounding boxes (DEBT-03 fixed)
  - assemble_mermaid_svg() producing 5-layer stacked use structure
  - VARIANT_IDS list with 12 IDs including eye-1..3
  - BODY_ID constant and body group in assembled SVG defs
affects: [09-dress-up-ui-rework, frontend-dressup-js]

tech-stack:
  added: []
  patterns:
    - "TDD with failing tests committed before implementation (RED then GREEN commits)"
    - "Non-overlapping vertical region layout: hair(0-290) > eyes(300-440) > acc(450-549) > tail(550-1024)"
    - "5-layer SVG stacking: tail(back) > body(static) > hair > eyes > acc(front)"
    - "base_traced_svg parameter added to assemble_mermaid_svg() for body group creation"

key-files:
  created: []
  modified:
    - src/mermaids/pipeline/prompts.py
    - src/mermaids/pipeline/edit.py
    - src/mermaids/pipeline/assemble.py
    - tests/test_masks.py
    - tests/test_assemble.py

key-decisions:
  - "Redesigned acc region to torso/collar zone (y 450-549) instead of top-of-head to achieve non-overlapping layout with hair region"
  - "5-layer stacking: tail at back, body always-visible static, hair mid, eyes front, accessories topmost"
  - "assemble_mermaid_svg() gains optional base_traced_svg parameter (backward compatible via None default)"
  - "Eye region placed at face-center y 300-440, deliberately narrower x range (300-724) than hair"

patterns-established:
  - "Variant prompts specify 'isolated part only, keep rest of character unchanged' to constrain edit API to region"
  - "Non-overlapping region layout by stacking vertically: hair crown -> eyes face -> acc collar -> tail lower"
  - "Body group always first in defs; variant groups follow in VARIANT_IDS order"
  - "active-body use element has no data-category attribute (static, UI never swaps it)"

requirements-completed: [DRSU-01, DRSU-02, DRSU-03, DRSU-04, DEBT-03]

duration: 25min
completed: 2026-03-12
---

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
