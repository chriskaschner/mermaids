---
phase: 07-github-pages-deployment
plan: 01
subsystem: infra
tags: [github-actions, playwright, pytest, static-server, ci-cd]

requires:
  - phase: 06-dress-up-art-swap
    provides: frontend static assets and E2E test suite

provides:
  - BASE_URL env var guard in live_server fixture (conftest.py)
  - CI test job using python -m http.server + Playwright before deploy
  - deploy job gated on test job via needs: [test]

affects:
  - 07-02-github-pages-deployment

tech-stack:
  added: [astral-sh/setup-uv@v4 (CI action)]
  patterns: [BASE_URL env var pattern for static-server CI testing, test-gates-deploy workflow pattern]

key-files:
  created: []
  modified:
    - tests/conftest.py
    - .github/workflows/deploy.yml

key-decisions:
  - "BASE_URL env var causes live_server to yield URL directly without starting uvicorn -- enables static server testing"
  - "test job uses python -m http.server 8080 with server readiness poll before running Playwright"
  - "deploy job has needs: [test] to gate deploy on E2E pass"
  - "Pre-existing sparkle test failures (test_tap_region_triggers_sparkle, test_sparkle_cleanup) deferred -- fail identically against uvicorn"

patterns-established:
  - "BASE_URL guard: if os.environ.get('BASE_URL'): yield base_url; return -- skip server startup in CI"
  - "CI static server: python -m http.server 8080 & + poll loop + BASE_URL=http://127.0.0.1:8080 pytest"

requirements-completed: [DPLY-01, DPLY-02, DPLY-03]

duration: 8min
completed: 2026-03-12
---

# Phase 7 Plan 01: CI Test Gate for GitHub Pages Deployment Summary

**CI test job using python -m http.server + Playwright E2E tests gates the deploy job, with BASE_URL env var allowing conftest.py live_server to skip uvicorn startup in static-server mode**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-12T00:59:57Z
- **Completed:** 2026-03-12T01:08:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Updated live_server fixture to yield BASE_URL directly when env var is set, enabling E2E tests against static servers without FastAPI/uvicorn
- Added CI test job to deploy.yml with static server startup, readiness polling, and Playwright E2E run
- Gated the deploy job on test job passing via needs: [test]
- Confirmed 60/62 E2E tests pass against python -m http.server (2 pre-existing failures unrelated to changes)

## Task Commits

Each task was committed atomically:

1. **Task 1: Update live_server fixture for BASE_URL env var** - `a234d2e` (feat)
2. **Task 2: Add test job to deploy.yml gating deploy** - `ce2fbb3` (feat)

## Files Created/Modified

- `tests/conftest.py` - Added `import os`; updated live_server fixture to yield BASE_URL env var if set
- `.github/workflows/deploy.yml` - Added test job with static server + Playwright; added `needs: [test]` to deploy job

## Decisions Made

- BASE_URL env var approach chosen: minimal change to conftest.py, works with any static server, zero overhead when not set
- test job polls for server readiness with curl before running tests (30 attempts with 1s sleep)
- deploy job kept unchanged except for `needs: [test]` addition

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Pre-existing test failures: `test_tap_region_triggers_sparkle[webkit]` and `test_sparkle_cleanup[webkit]` fail against both uvicorn and python -m http.server. Root cause: `[data-region="tail"]` locator not found in dressup view during webkit. Deferred to deferred-items.md. These 2 failures are not caused by this plan's changes and do not affect the deployment gate logic.

## Next Phase Readiness

- CI pipeline ready: push to main will run E2E tests against static server before deploying
- Plan 07-02 can proceed (custom domain / additional GitHub Pages configuration)
- The 2 pre-existing sparkle test failures will cause the CI test job to fail until resolved

---
*Phase: 07-github-pages-deployment*
*Completed: 2026-03-12*
