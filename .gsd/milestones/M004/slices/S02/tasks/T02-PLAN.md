---
estimated_steps: 3
estimated_files: 1
skills_used:
  - test
  - best-practices
---

# T02: Add icon semantic E2E tests and validate ICON-01

**Slice:** S02 — Icon Refresh
**Milestone:** M004

## Description

Add a `TestIconSemantics` test class to `tests/test_e2e.py` that asserts all nav bar and home screen icons have correct semantic attributes (aria-labels are present, distinct, and SVG elements exist). Then mark the ICON-01 requirement as validated. These are DOM assertion tests using the existing `app_page` Playwright fixture — no visual rendering comparison needed.

## Steps

1. **Add `class TestIconSemantics` to `tests/test_e2e.py`** — Place it after the existing `TestTapTargets` class (around line 138). Use the same `app_page` fixture. Add these test methods:

   - `test_nav_icons_have_aria_labels(self, app_page)` — Assert each `.nav-icon` element has a non-empty `aria-label` attribute. Use `app_page.locator(".nav-icon")` and iterate, calling `get_attribute("aria-label")`.

   - `test_nav_icon_labels_are_distinct(self, app_page)` — Collect all `.nav-icon` aria-labels into a list, assert `len(labels) == len(set(labels))` (no duplicates).

   - `test_nav_icons_contain_svg(self, app_page)` — Assert each `.nav-icon` contains at least one `<svg>` child element. Use `locator.locator("svg").count() >= 1`.

   - `test_activity_buttons_have_svg_and_labels(self, app_page)` — Assert each `.activity-btn` on the home view has a non-empty `aria-label` and contains an `<svg>` child. Expected labels: "Dress Up" and "Coloring".

2. **Run the new tests** — Execute `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py::TestIconSemantics -x -v` and confirm all pass.

3. **Run the full test suite** — Execute `.venv/bin/python -m pytest tests/ -x -q` and confirm 111+ tests pass (no regressions, new tests add to count).

## Must-Haves

- [ ] `TestIconSemantics` class exists in `tests/test_e2e.py` with 3+ test methods
- [ ] All new tests pass
- [ ] Full test suite stays at 111+ tests passing
- [ ] Tests assert aria-label presence, distinctness, and SVG child presence

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_e2e.py::TestIconSemantics -x -v` — all new tests pass
- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/ -x -q` — 111+ tests passing
- `grep -c "class TestIconSemantics" tests/test_e2e.py` returns 1

## Inputs

- `tests/test_e2e.py` — Existing E2E test file with `app_page` fixture, `TestTapTargets` class at line ~114. T01 must be complete so the mermaid tail icons are in place.
- `frontend/index.html` — Nav bar with aria-labels on `.nav-icon` elements (read by tests, not modified)
- `frontend/js/app.js` — Home view with aria-labels on `.activity-btn` elements (read by tests, not modified)

## Expected Output

- `tests/test_e2e.py` — New `TestIconSemantics` class with 4 test methods added
