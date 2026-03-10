---
phase: 04-art-pipeline
plan: 02
subsystem: pipeline
tags: [openai, gpt-image-1, edit-api, pillow, svg, assembly, masks, dressup]

# Dependency graph
requires:
  - phase: 04-art-pipeline
    plan: 01
    provides: "Pipeline config, prompts, generate_image(), retry_api_call(), trace scripts"
provides:
  - "Mask creation for OpenAI edit API (RGBA transparent-region masks)"
  - "Dress-up variant generation: base mermaid + 9 variants via edit API"
  - "SVG assembly into defs+use mermaid.svg matching frontend pattern"
  - "Frontend asset copy utilities (coloring SVGs and mermaid.svg)"
  - "Full pipeline orchestrator running all stages end-to-end"
affects: [05-flood-fill-coloring, 06-dressup-art-swap]

# Tech tracking
tech-stack:
  added: []
  patterns: [edit-api-with-masks, rgba-mask-creation, svg-defs-use-assembly, pipeline-orchestrator]

key-files:
  created:
    - src/mermaids/pipeline/edit.py
    - src/mermaids/pipeline/assemble.py
    - scripts/generate_dressup.py
    - scripts/assemble_mermaid.py
    - scripts/run_pipeline.py
    - tests/test_masks.py
    - tests/test_assemble.py
  modified: []

key-decisions:
  - "Separate _get_client() in edit.py from generate.py for independent mocking"
  - "Skip watercolor filter for kawaii style -- flat cell-shaded output does not benefit from noise displacement"
  - "Body group and face details are hardcoded SVG elements (not from traced parts) since they do not vary"
  - "Variant groups get scale transform (400/1024, 700/1024) to fit traced 1024px output into 400x700 viewBox"

patterns-established:
  - "Edit API pattern: create_region_mask() -> edit_region() -> generate_dressup_variants() pipeline"
  - "SVG assembly: ET.Element construction with namespace, defs+use, body group, face details"
  - "Pipeline orchestrator: 7 idempotent stages called in sequence, each printing progress"

requirements-completed: [ARTP-03, ARTP-04]

# Metrics
duration: 5min
completed: 2026-03-10
---

# Phase 4 Plan 2: Dress-up Variant Generation and SVG Assembly Summary

**Edit API mask-based dress-up generation (9 variants) and defs+use SVG assembly with full pipeline orchestrator, backed by 17 new tests**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-10T00:40:15Z
- **Completed:** 2026-03-10T00:45:12Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Mask creation and edit API integration: create_region_mask() produces RGBA masks with transparent regions for tail/hair/accessories, edit_region() wraps OpenAI images.edit with retry and skip logic, generate_dressup_variants() produces base mermaid + 9 variant PNGs
- SVG assembly pipeline: assemble_mermaid_svg() builds valid XML with defs containing all 10 variant groups (9 parts + acc-none), use elements for active-tail/hair/acc, body group with torso/arms/shell, face details (eyes/sparkles/smile/cheeks)
- Full pipeline orchestrator: run_pipeline.py executes 7 stages (generate coloring, generate dressup, trace coloring, trace dressup, assemble, copy coloring, copy mermaid) with stage-by-stage progress output

## Task Commits

Each task was committed atomically:

1. **Task 1: Mask creation and dress-up variant generation via edit API**
   - `3424e5d` (test) - Failing tests for mask creation and dressup generation
   - `9a020af` (feat) - Implementation: edit.py, generate_dressup.py, 7 tests green

2. **Task 2: SVG assembly, frontend asset copy, and pipeline orchestrator**
   - `1134fa8` (test) - Failing tests for SVG assembly and copy functions
   - `e2d1eee` (feat) - Implementation: assemble.py, assemble_mermaid.py, run_pipeline.py, 10 tests green

## Files Created/Modified
- `src/mermaids/pipeline/edit.py` - Mask creation (create_region_mask), edit API wrapper (edit_region), base generation (generate_base_mermaid), full variant generation (generate_dressup_variants)
- `src/mermaids/pipeline/assemble.py` - SVG assembly (assemble_mermaid_svg) with defs+use structure, copy utilities (copy_coloring_pages_to_frontend, copy_mermaid_to_frontend)
- `scripts/generate_dressup.py` - CLI entry point for dress-up base + variant generation
- `scripts/assemble_mermaid.py` - CLI entry point for SVG assembly and frontend copy
- `scripts/run_pipeline.py` - Full pipeline orchestrator running all 7 stages in sequence
- `tests/test_masks.py` - 7 tests for mask creation, base generation, edit region, full variant pipeline
- `tests/test_assemble.py` - 10 tests for SVG structure, variant IDs, use elements, body, face, viewBox, copy functions

## Decisions Made
- Separate OpenAI client cache in edit.py from generate.py, allowing independent mocking in tests
- Skipped watercolor filter for kawaii style -- flat cell-shaded AI output does not benefit from fractalNoise displacement
- Body group and face details are hardcoded SVG (copied from existing mermaid.svg) since they are constant across all dress-up combinations
- Applied scale transform (0.3906, 0.6836) to variant groups mapping 1024x1024 traced output to 400x700 viewBox

## Deviations from Plan

None - plan executed exactly as written.

## User Setup Required

**External services require manual configuration:**
- **OPENAI_API_KEY** environment variable needed before running scripts/generate_dressup.py or scripts/run_pipeline.py
- Get key from: https://platform.openai.com/api-keys

## Issues Encountered
None.

## Next Phase Readiness
- Art pipeline complete: all generation, tracing, assembly, and deployment scripts functional
- Frontend assets will be populated when API key is configured and scripts/run_pipeline.py is executed
- Phase 5 (flood fill coloring) can proceed using coloring SVGs in frontend/assets/svg/coloring/
- Phase 6 (dressup art swap) can proceed using mermaid.svg with defs+use structure in frontend/assets/svg/
- 29 total tests passing across the full pipeline test suite

## Self-Check: PASSED

All 7 created files verified present. All 4 task commits verified in git history.

---
*Phase: 04-art-pipeline*
*Completed: 2026-03-10*
