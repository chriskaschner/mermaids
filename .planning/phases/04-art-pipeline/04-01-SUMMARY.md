---
phase: 04-art-pipeline
plan: 01
subsystem: pipeline
tags: [openai, gpt-image-1, vtracer, pillow, svg, generation, tracing]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "trace.py vtracer wrapper with trace_to_svg()"
provides:
  - "Pipeline config module with shared paths and retry constants"
  - "Prompt templates for coloring and dress-up generation"
  - "OpenAI image generation with retry and idempotent skip"
  - "CLI scripts for coloring page generation and PNG-to-SVG tracing"
affects: [04-02, 05-flood-fill-coloring, 06-dressup-art-swap]

# Tech tracking
tech-stack:
  added: [openai>=2.0]
  patterns: [retry-with-exponential-backoff, idempotent-file-generation, module-level-client-cache]

key-files:
  created:
    - src/mermaids/pipeline/config.py
    - src/mermaids/pipeline/prompts.py
    - src/mermaids/pipeline/generate.py
    - scripts/generate_coloring.py
    - scripts/trace_all.py
    - tests/test_generate.py
    - tests/test_trace_coloring.py
  modified:
    - pyproject.toml

key-decisions:
  - "retry_api_call wraps both RateLimitError and APIError with 1+max_retries attempts and exponential backoff"
  - "Module-level cached OpenAI client via _get_client() avoids repeated instantiation"
  - "scripts/ kept as standalone files loaded via importlib in tests, not installed as a package"

patterns-established:
  - "Pipeline module pattern: config.py for constants, prompts.py for templates, generate.py for API calls"
  - "Idempotent generation: check output_path.exists() before API call"
  - "TDD with mocked OpenAI client: patch _get_client() and provide mock response with b64_json"

requirements-completed: [ARTP-01, ARTP-02]

# Metrics
duration: 4min
completed: 2026-03-10
---

# Phase 4 Plan 1: Shared Pipeline Infra + Coloring Page Generation Summary

**OpenAI gpt-image-1 generation pipeline with retry/idempotency and vtracer coloring page tracing, backed by 12 tests using mocked API**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-10T00:33:33Z
- **Completed:** 2026-03-10T00:37:40Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Pipeline infrastructure: config.py with shared paths/constants, prompts.py with coloring and dress-up templates, generate.py with idempotent OpenAI generation and exponential backoff retry
- CLI scripts: generate_coloring.py calls generate_coloring_pages() for 4 coloring page PNGs, trace_all.py traces PNGs to SVGs with binary mode for clean outlines
- Full test coverage: 8 tests for generation logic (API calls, skip, retry, batch) + 4 tests for tracing (SVG validity, binary mode, size limit, skip existing) + 5 existing pipeline tests all green

## Task Commits

Each task was committed atomically:

1. **Task 1: Pipeline shared modules and test scaffolds** - `b119668` (feat)
2. **Task 2: Coloring page tracing script and integration test** - `30770bc` (feat)

## Files Created/Modified
- `pyproject.toml` - Added openai>=2.0 dependency
- `src/mermaids/pipeline/config.py` - Shared path constants (GENERATED_PNG_DIR, GENERATED_SVG_DIR, FRONTEND_SVG_DIR) and retry settings
- `src/mermaids/pipeline/prompts.py` - COLORING_BASE_PROMPT, COLORING_PAGES (4 pages), DRESSUP_BASE_PROMPT, DRESSUP_VARIANTS (tails/hair/accessories)
- `src/mermaids/pipeline/generate.py` - generate_image() with retry and skip, generate_coloring_pages() for batch generation
- `scripts/generate_coloring.py` - CLI entry point for coloring page generation
- `scripts/trace_all.py` - CLI entry point for tracing PNGs to SVGs (coloring + dressup stub)
- `tests/test_generate.py` - 8 tests covering generation, config, and prompts
- `tests/test_trace_coloring.py` - 4 tests covering tracing and skip logic

## Decisions Made
- retry_api_call uses 1 initial attempt + up to RETRY_MAX retries (total 4 attempts) with exponential backoff on both RateLimitError and APIError
- Module-level cached OpenAI client via _get_client() to avoid repeated instantiation
- scripts/ directory has __init__.py but tests import via importlib.util.spec_from_file_location since scripts aren't an installed package

## Deviations from Plan

None - plan executed exactly as written.

## User Setup Required

**External services require manual configuration:**
- **OPENAI_API_KEY** environment variable needed before running `scripts/generate_coloring.py`
- Get key from: https://platform.openai.com/api-keys

## Issues Encountered
- pytest not found in venv despite being in dev deps; resolved by installing directly via uv pip install pytest

## Next Phase Readiness
- Pipeline infrastructure ready for Plan 02 (dress-up variant generation via edit API)
- DRESSUP_BASE_PROMPT and DRESSUP_VARIANTS already defined in prompts.py
- trace_dressup_parts() stub in trace_all.py ready for implementation
- All 17 tests pass (test_generate + test_trace_coloring + test_pipeline)

## Self-Check: PASSED

All 8 created files verified present. Both task commits (b119668, 30770bc) verified in git history.

---
*Phase: 04-art-pipeline*
*Completed: 2026-03-10*
