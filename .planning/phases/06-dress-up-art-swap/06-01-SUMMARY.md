---
phase: 06-dress-up-art-swap
plan: 01
subsystem: pipeline
tags: [svg, vtracer, assembly, defs-use, background-strip]

# Dependency graph
requires:
  - phase: 04-ai-art
    provides: "Traced SVGs in assets/generated/svg/dressup/ (9 variant parts)"
provides:
  - "copy_dressup_parts_to_frontend() for deploying individual variant SVGs"
  - "_is_background_path() heuristic for detecting vtracer near-white background rects"
  - "Background-rect stripping in _make_variant_group()"
  - "9 variant SVGs in frontend/assets/svg/dressup/ for preview thumbnails"
  - "Regenerated mermaid.svg with AI-generated parts, background rects stripped"
affects: [06-dress-up-art-swap]

# Tech tracking
tech-stack:
  added: []
  patterns: [background-path-detection-heuristic, copy-to-frontend-pattern]

key-files:
  created:
    - frontend/assets/svg/dressup/tail-1.svg
    - frontend/assets/svg/dressup/tail-2.svg
    - frontend/assets/svg/dressup/tail-3.svg
    - frontend/assets/svg/dressup/hair-1.svg
    - frontend/assets/svg/dressup/hair-2.svg
    - frontend/assets/svg/dressup/hair-3.svg
    - frontend/assets/svg/dressup/acc-1.svg
    - frontend/assets/svg/dressup/acc-2.svg
    - frontend/assets/svg/dressup/acc-3.svg
  modified:
    - src/mermaids/pipeline/assemble.py
    - tests/test_assemble.py
    - frontend/assets/svg/mermaid.svg

key-decisions:
  - "Near-white background detection uses RGB component threshold >= 0xF0, not just #FEFEFE prefix match"
  - "Only 2 of 9 traced SVGs (hair-3, tail-3) had near-white background rects; others had dark first paths that are real content"

patterns-established:
  - "_is_background_path() heuristic: path tag + near-white fill (all RGB >= 0xF0) + d starts at M0 0"
  - "copy_dressup_parts_to_frontend() follows same pattern as copy_coloring_pages_to_frontend()"

requirements-completed: [DRSV-01, DRSV-02]

# Metrics
duration: 3min
completed: 2026-03-10
---

# Phase 6 Plan 01: Deploy AI-generated kawaii SVG assets to frontend with background-rect stripping

**9 variant SVGs deployed to frontend/assets/svg/dressup/ with vtracer background rects stripped from assembled mermaid.svg using near-white fill heuristic**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-10T02:39:52Z
- **Completed:** 2026-03-10T02:42:30Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments
- Added _is_background_path() heuristic and background-rect stripping in _make_variant_group()
- Added copy_dressup_parts_to_frontend() function following existing copy pattern
- Deployed 9 individual variant SVGs for preview thumbnails
- Regenerated mermaid.svg with 10 variant groups in defs, all background rects stripped
- 14 unit tests all green (4 new: TestCopyDressupParts x2, TestBackgroundStrip x2)

## Task Commits

Each task was committed atomically:

1. **Task 1: Strip background rect + add copy function** - `df161b0` (test) -> `4482206` (feat, TDD)
2. **Task 2: Deploy variant SVGs and regenerate mermaid.svg** - `6d1aebc` (feat)

_Note: Task 1 used TDD with separate RED and GREEN commits_

## Files Created/Modified
- `src/mermaids/pipeline/assemble.py` - Added _is_background_path(), background strip in _make_variant_group(), copy_dressup_parts_to_frontend()
- `tests/test_assemble.py` - Added TestCopyDressupParts (2 tests) and TestBackgroundStrip (2 tests)
- `frontend/assets/svg/dressup/tail-{1,2,3}.svg` - Individual tail variant SVGs for preview thumbnails
- `frontend/assets/svg/dressup/hair-{1,2,3}.svg` - Individual hair variant SVGs for preview thumbnails
- `frontend/assets/svg/dressup/acc-{1,2,3}.svg` - Individual accessory variant SVGs for preview thumbnails
- `frontend/assets/svg/mermaid.svg` - Regenerated assembled mermaid with AI-generated parts, bg rects stripped

## Decisions Made
- Near-white background detection uses RGB component threshold (all >= 0xF0) rather than simple prefix match, because real traced SVGs may have #FEFEFE or similar fills
- Only strip the first child if it matches the heuristic -- other near-white paths later in the SVG could be legitimate content
- Only 2 of 9 SVGs actually had the near-white background rect; the rest had dark-colored first paths that are real content

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness
- All 9 variant SVGs deployed to frontend serving directory
- Assembled mermaid.svg ready for dressup.js to swap variant groups
- Ready for Plan 02: frontend JS integration for dress-up part swapping

## Self-Check: PASSED

All 12 files verified present. All 3 commits (df161b0, 4482206, 6d1aebc) verified in git log.

---
*Phase: 06-dress-up-art-swap*
*Completed: 2026-03-10*
