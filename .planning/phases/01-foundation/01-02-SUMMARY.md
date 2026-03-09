---
phase: 01-foundation
plan: 02
subsystem: pipeline
tags: [vtracer, svg, pillow, art-pipeline, touch-regions]

# Dependency graph
requires:
  - phase: 01-foundation-01
    provides: "pyproject.toml with vtracer and Pillow dependencies, src/mermaids package"
provides:
  - "trace_to_svg() function for raster-to-SVG conversion via vtracer"
  - "Proof-of-concept mermaid SVG with 3 tappable regions (hair, body, tail)"
  - "Watercolor SVG filter definition"
  - "Pipeline test suite (5 tests)"
affects: [01-foundation-03, 02-dress-up]

# Tech tracking
tech-stack:
  added: [vtracer, pillow]
  patterns: [vtracer-tracing, svg-tappable-regions, watercolor-filter, invisible-hit-areas]

key-files:
  created:
    - src/mermaids/pipeline/__init__.py
    - src/mermaids/pipeline/trace.py
    - frontend/assets/svg/mermaid.svg
    - tests/test_pipeline.py
  modified: []

key-decisions:
  - "vtracer returns SVG string via convert_image_to_svg_py with out_path parameter, not as return value"
  - "Proof-of-concept SVG is hand-crafted (not pipeline-traced) to guarantee correct region structure"
  - "Face details rendered outside watercolor filter for clarity"

patterns-established:
  - "SVG tappable regions: <g data-region='name' pointer-events='all'> with invisible hit-area <rect>"
  - "Watercolor filter: feTurbulence + feDisplacementMap + fine-noise feComposite in <defs>"
  - "Pipeline function signature: trace_to_svg(input_path, output_path, *, simplify=True) -> Path"

requirements-completed: [FOUN-03]

# Metrics
duration: 3min
completed: 2026-03-09
---

# Phase 1 Plan 2: Art Pipeline Summary

**vtracer raster-to-SVG pipeline with simplify/color modes, plus hand-crafted proof-of-concept mermaid SVG with 3 tappable regions and watercolor filter**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-09T17:19:13Z
- **Completed:** 2026-03-09T17:22:51Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- trace_to_svg() converts raster images to SVG with automatic resize (>1024px) and configurable simplification (binary vs color mode)
- Proof-of-concept mermaid SVG with 3 named tappable regions (hair/body/tail), each with invisible hit-area rects exceeding 60pt minimum
- Watercolor SVG filter (feTurbulence + feDisplacementMap) defined in defs and applied to all mermaid art
- 5 pipeline tests all passing: valid SVG output, file size limit, XML validity, simplify flag, large image resize

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Failing pipeline tests** - `dff38cc` (test)
2. **Task 1 (GREEN): trace_to_svg implementation** - `4fc5e12` (feat)
3. **Task 2: Mermaid SVG with tappable regions** - `ebab869` (feat)

_Note: Task 1 followed TDD with RED/GREEN commits._

## Files Created/Modified
- `src/mermaids/pipeline/__init__.py` - Package init for pipeline module
- `src/mermaids/pipeline/trace.py` - vtracer wrapper: trace_to_svg() with resize, simplify, temp file management
- `frontend/assets/svg/mermaid.svg` - Proof-of-concept mermaid with 3 tappable regions, watercolor filter, 5.4KB
- `tests/test_pipeline.py` - 5 tests: valid SVG, size limit, XML, simplify paths, resize

## Decisions Made
- Used vtracer's `out_path` parameter (writes file directly) rather than capturing return value as string
- Hand-crafted the proof-of-concept SVG rather than running it through the trace pipeline -- the pipeline was validated in Task 1, but the PoC needs specific structure (named groups, hit areas, face details) that manual creation guarantees
- Rendered face details (eyes, smile, cheeks) outside the watercolor filter group for visual clarity
- Hit-area rects sized generously: hair 120x130, body 160x230, tail 180x330 -- all well above 60pt minimum

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] vtracer API uses out_path parameter, not return value**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** Plan's code example showed vtracer returning SVG as string; actual API writes directly to file via out_path parameter
- **Fix:** Changed implementation to use out_path parameter instead of capturing return value
- **Files modified:** src/mermaids/pipeline/trace.py
- **Verification:** All 5 tests pass
- **Committed in:** 4fc5e12

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minor API correction. No scope creep.

## Issues Encountered
None -- plan 01-01's scaffolding (pyproject.toml, uv.lock, dependencies) was already present from a prior partial execution.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- trace_to_svg() is ready for use with real AI-generated art assets
- mermaid.svg is ready for plan 03 to wire touch events and sparkle feedback
- The watercolor filter pattern is established for reuse across all SVG assets

## Self-Check: PASSED

- All 5 files confirmed present on disk
- All 3 commits confirmed in git history (dff38cc, 4fc5e12, ebab869)
- All 5 pipeline tests pass

---
*Phase: 01-foundation*
*Completed: 2026-03-09*
