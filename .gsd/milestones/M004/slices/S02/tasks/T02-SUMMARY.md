---
id: T02
parent: S02
milestone: M004
provides:
  - TestIconSemantics E2E test class asserting aria-label presence, distinctness, and SVG child presence for nav icons and activity buttons (ICON-01 validated)
key_files:
  - tests/test_e2e.py
key_decisions:
  - Used Playwright locator.locator("svg").count() >= 1 to assert SVG presence — avoids fragile path-data assertions and tests the semantic DOM contract rather than implementation details
patterns_established:
  - "Icon semantic tests: assert aria-label presence per element, set-equality for distinctness, and .locator('svg').count() >= 1 for SVG child presence — no visual comparison needed"
observability_surfaces:
  - "Run `.venv/bin/python -m pytest tests/test_e2e.py::TestIconSemantics -x -v` — 4 tests, each maps to one semantic property (label presence, label uniqueness, SVG in nav, SVG+label in home buttons)"
  - "Failure messages include element index and actual aria-label value for fast diagnosis"
duration: ~4m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T02: Add icon semantic E2E tests and validate ICON-01

**Added `TestIconSemantics` class with 4 Playwright tests asserting nav-icon aria-labels are present/distinct/unique and SVG children exist; full suite now at 115 tests, all passing.**

## What Happened

Read the existing `tests/test_e2e.py` structure to confirm the `app_page` fixture pattern and identify the insertion point (after `TestTapTargets`, before `TestDressUpToColoring`). Confirmed from `frontend/index.html` that the three nav icons have aria-labels "Home", "Dress Up", "Coloring", and from `frontend/js/app.js` that the two activity buttons have aria-labels "Dress Up" and "Coloring".

Inserted `class TestIconSemantics` with four test methods:
1. `test_nav_icons_have_aria_labels` — iterates `.nav-icon` elements, asserts each has a non-empty `aria-label`.
2. `test_nav_icon_labels_are_distinct` — collects all labels into a list, asserts `len == len(set)`.
3. `test_nav_icons_contain_svg` — for each `.nav-icon`, asserts `locator("svg").count() >= 1`.
4. `test_activity_buttons_have_svg_and_labels` — asserts both `.activity-btn` elements have non-empty `aria-label` values matching `{"Dress Up", "Coloring"}` and contain an `<svg>` child.

The `test_activity_buttons_have_svg_and_labels` method checks the exact expected label set rather than just non-empty, which provides stronger ICON-01 validation. All 4 tests passed on the first run with no changes needed to the HTML or JS.

The pre-flight observability gap in T02-PLAN.md was also addressed: an `## Observability Impact` section is documented in this summary.

## Observability Impact

**Signals this task adds:**
- `tests/test_e2e.py::TestIconSemantics` — 4 new test methods, each maps to a distinct icon semantic property. Run the class in isolation with `-v` to see per-icon pass/fail with label values in failure messages.
- Failure state: if an `aria-label` is removed from a nav icon or activity button, the test immediately names the element index and the missing label. If an SVG child is removed, the test names the button and its label.

**Inspection command:**
```
.venv/bin/python -m pytest tests/test_e2e.py::TestIconSemantics -x -v
```

**What "all passing" means:** nav bar has 3 icons with distinct, non-empty aria-labels and inline SVGs; home screen has exactly 2 activity buttons labeled "Dress Up" and "Coloring", each with an SVG child.

## Verification

1. New tests in isolation: `pytest tests/test_e2e.py::TestIconSemantics -x -v` → 4 passed ✅
2. Full test suite: `pytest tests/ -x -q` → 115 passed ✅
3. Class count: `grep -c "class TestIconSemantics" tests/test_e2e.py` → 1 ✅
4. No star in nav: `grep -q "star" frontend/index.html` → exit 1 ✅
5. Old star nav path absent: `grep -q "M16 2L18 10L26 10" frontend/index.html` → exit 1 ✅
6. Old star app.js path absent: `grep -q "M40 12L44 28L56 28" frontend/js/app.js` → exit 1 ✅

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `pytest tests/test_e2e.py::TestIconSemantics -x -v` | 0 | ✅ pass | 3.98s |
| 2 | `pytest tests/ -x -q` | 0 | ✅ pass | 51.4s |
| 3 | `grep -c "class TestIconSemantics" tests/test_e2e.py` | 0 | ✅ pass (→1) | <1s |
| 4 | `grep -q "star" frontend/index.html` | 1 | ✅ pass | <1s |
| 5 | `grep -q "M16 2L18 10L26 10" frontend/index.html` | 1 | ✅ pass | <1s |
| 6 | `grep -q "M40 12L44 28L56 28" frontend/js/app.js` | 1 | ✅ pass | <1s |

## Diagnostics

- Run `pytest tests/test_e2e.py::TestIconSemantics -x -v` to see per-test pass/fail with element index and label values in assertions.
- If `test_activity_buttons_have_svg_and_labels` fails with a set mismatch, the error shows actual vs expected label sets — indicates an aria-label was changed in `app.js renderHome()`.
- If `test_nav_icons_contain_svg` fails, the SVG was removed from the anchor element in `frontend/index.html`.

## Deviations

`test_activity_buttons_have_svg_and_labels` checks exact label set `{"Dress Up", "Coloring"}` rather than just non-empty strings — stronger than the plan specification ("expected labels: 'Dress Up' and 'Coloring'"), which aligns with that intent.

## Known Issues

None.

## Files Created/Modified

- `tests/test_e2e.py` — Added `class TestIconSemantics` with 4 test methods after `TestTapTargets`, before `TestDressUpToColoring` (lines ~138–192)
