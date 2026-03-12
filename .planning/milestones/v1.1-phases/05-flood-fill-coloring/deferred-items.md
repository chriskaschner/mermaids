# Deferred Items - Phase 05

## Pre-existing Test Failure

**File:** `tests/test_e2e.py::TestTouchInteraction::test_tap_region_triggers_sparkle`
**Issue:** Test fails with timeout on clicking `[data-region="tail"]` -- the `<use>` element for hair intercepts pointer events, blocking the tail click. This is a pre-existing issue (verified by reverting Phase 05 changes and reproducing the same failure).
**Impact:** Low -- dress-up sparkle feedback, not related to coloring feature.
**Recommendation:** Fix in dress-up E2E test by using force-click or adjusting SVG element ordering.
