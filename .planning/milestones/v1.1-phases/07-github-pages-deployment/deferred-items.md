---
phase: 07-github-pages-deployment
plan: 01
date: 2026-03-12
---

# Deferred Items

## Pre-existing Test Failures (out of scope)

### test_tap_region_triggers_sparkle[webkit] and test_sparkle_cleanup[webkit]

- **Found during:** Task 1 verification
- **Status:** Pre-existing — fails identically against uvicorn and python -m http.server
- **Symptom:** `[data-region="tail"]` locator not found in dressup view
- **Impact:** 2 of 62 E2E tests fail; all other tests pass
- **Action:** Deferred — not caused by 07-01 changes
