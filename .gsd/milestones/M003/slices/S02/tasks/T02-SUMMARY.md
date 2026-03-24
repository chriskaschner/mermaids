---
id: T02
parent: S02
milestone: M003
provides:
  - Debug overlay (_initDebug function, ?debug=1 wiring, triple-tap wiring) fully removed from app.js
  - DEBT-02 (WebKit sparkle E2E failures) confirmed already fixed — 2 WebKit tests pass
  - All slice verification checks passing with 103 tests total
key_files:
  - frontend/js/app.js
key_decisions:
  - Removed entire _initDebug function block (~85 lines) and all its activation wiring in a single pass without introducing replacement stubs
patterns_established:
  - After removing dead code, always run three grep-negation checks (_initDebug, debug=1, tapCount) before running full test suite — fast local confirmation before spending 50s on E2E
observability_surfaces:
  - "grep -q '_initDebug' frontend/js/app.js (must exit 1 — signal that debug overlay is absent)"
  - "uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit (DEBT-02 signal)"
  - "uv run pytest -q (full suite; 103 passed is baseline)"
duration: ~10m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T02: Remove debug overlay and confirm DEBT-02 already fixed

**Removed the entire `_initDebug` debug overlay and all activation wiring from `app.js`; confirmed DEBT-02 already fixed with 2 WebKit sparkle tests passing; full suite holds at 103 passed.**

## What Happened

The `_initDebug()` function (~85 lines including JSDoc) and all three activation paths were removed from `frontend/js/app.js` in two surgical edits:

1. **Removed the debug overlay section** — Deleted the `// -- Debug overlay ---` comment block, JSDoc, and the entire `_initDebug()` function body, which created a fixed-position monospace event log overlay intended for iPad Safari debugging. The removal left the `// -- Router --` section immediately following.

2. **Removed DOMContentLoaded wiring** — Deleted the `if (window.location.search.includes("debug=1")) { _initDebug(); }` block and the triple-tap wiring block (`homeNavIcon`, `tapCount`, `tapTimer`, and the capture-phase click listener). The DOMContentLoaded handler now contains only the hash-routing bootstrap logic.

3. **Confirmed DEBT-02** — Ran `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit` which produced 2 passed (sparkle trigger + cleanup). No code changes required — pre-existing fix is confirmed.

The pre-flight observability gap flags for S02-PLAN.md and T02-PLAN.md were addressed by adding `## Observability / Diagnostics` to S02-PLAN.md.

## Verification

Three grep-negation checks confirmed zero remaining references before running tests:
- `! grep -q "_initDebug" frontend/js/app.js` → PASS
- `! grep -q "debug=1" frontend/js/app.js` → PASS
- `! grep -q "tapCount" frontend/js/app.js` → PASS

All E2E tests pass on Chromium (10/10), WebKit sparkle tests pass (2/2), and the full suite passes 103 tests.

Slice-level checks:
- `grep -c "page-" src/mermaids/pipeline/prompts.py` → 9 ✅
- `grep -c "page-" frontend/js/coloring.js` → 9 ✅
- `! grep -q "_initDebug" frontend/js/app.js` → PASS ✅

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `! grep -q "_initDebug" frontend/js/app.js` | 0 | ✅ pass | <1s |
| 2 | `! grep -q "debug=1" frontend/js/app.js` | 0 | ✅ pass | <1s |
| 3 | `! grep -q "tapCount" frontend/js/app.js` | 0 | ✅ pass | <1s |
| 4 | `uv run pytest tests/test_e2e.py -v` (Chromium) | 0 | ✅ 10/10 pass | 13.33s |
| 5 | `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit` | 0 | ✅ 2/2 pass | 9.21s |
| 6 | `uv run pytest -q` | 0 | ✅ 103 passed | 48.85s |

## Diagnostics

To verify debug overlay is absent at any time:
- `grep -q "_initDebug" frontend/js/app.js && echo REGRESSION || echo OK`

To confirm DEBT-02 (WebKit sparkle) remains fixed:
- `uv run pytest tests/test_e2e.py::TestTouchInteraction -v --browser webkit`

To confirm overall E2E health after app.js changes:
- `uv run pytest tests/test_e2e.py -v`

## Deviations

- **S02-PLAN.md observability gap** — Added `## Observability / Diagnostics` section to the slice plan as required by the pre-flight flags. This was not in the task plan steps but was required by the pre-flight observability gap instructions.

## Known Issues

- Pages 5-9 still have no SVG art files (`assets/svg/coloring/page-N-*.svg`). This is expected and noted in S02 Integration Closure — requires `uv run python scripts/generate_coloring.py` + `scripts/trace_all.py` with an OpenAI API key.

## Files Created/Modified

- `frontend/js/app.js` — Removed `_initDebug()` function (~85 lines), `?debug=1` activation block, and triple-tap wiring from DOMContentLoaded handler
- `.gsd/milestones/M003/slices/S02/S02-PLAN.md` — Added `## Observability / Diagnostics` section; marked T02 complete
