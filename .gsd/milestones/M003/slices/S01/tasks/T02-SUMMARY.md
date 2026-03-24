---
id: T02
parent: S01
milestone: M003
provides: []
requires: []
affects: []
key_files: []
key_decisions: []
patterns_established: []
observability_surfaces: []
drill_down_paths: []
duration: 
verification_result: passed
completed_at: 
blocker_discovered: false
---
# T02: 08-dress-up-art-rework 02

**# Phase 8 Plan 02: Dress-Up Frontend Rework Summary**

## What Happened

# Phase 8 Plan 02: Dress-Up Frontend Rework Summary

**One-liner:** Multi-part independent layer swapping with eyes category, per-part recoloring, and 5-tab UI replacing single-character swap approach.

## What Was Built

Reworked the dress-up frontend from "swap between full characters" to "swap individual parts independently." Each category (hair, eyes, tail, acc) now has its own `<use>` element in the SVG that swaps only its layer. Color recoloring applies to the active category's current part only, not the entire character.

### Key Changes

**dressup.js:** Complete logic rework.
- `PARTS` expanded to include `eyes: ["eye-1", "eye-2", "eye-3"]`
- `state` object: removed `activeCharacter`, added `eyes` field; all 4 categories tracked independently
- `swapPart(category, variantId)`: now targets `active-${category}` use element (e.g., `active-hair`), leaves all other layers unchanged
- `recolorActivePart(color)`: applies to `state[lastPartCategory]`'s source group only (not whole character)
- `checkCompletion()`: requires all 4 categories non-default (was 3)
- `resetState()`: includes `eyes = "eye-1"`, `activeCategory = "hair"`
- `initDressUp()`: renders `hair` options by default (matches first active tab)

**app.js:** Tab order updated.
- 5 tabs in order: Hair (active) > Eyes > Tail > Acc > Color + Undo
- Eyes tab has oval+circle SVG icon as specified in CONTEXT.md
- Hair tab is now the default active tab (was Tail)

**mermaid.svg:** SVG structure updated.
- Added `eye-1`, `eye-2`, `eye-3` groups to `<defs>` (geometric stubs for now)
- Added `<g id="body">` stub
- Replaced single `<use id="active-character">` with 5 stacked use elements: `active-tail`, `active-body`, `active-hair`, `active-eyes`, `active-acc`

**tests/test_dressup.py:** Full test rewrite.
- Added `TestEyeCategory`: eye tab visibility, swap isolation, 3 options count
- Updated `TestPartSwapping`: each test now verifies ONLY the target layer changes
- Updated `TestColorRecolor`: verifies per-category recoloring (active part only)
- Updated `TestSelectionPanel`: expects 5 tabs, hair tab default active
- Updated `TestCompletion`: requires all 4 categories for celebration
- Updated `TestDressUpView`: checks multi-use structure (active-hair/eyes/tail/acc)

## Test Results

22 dress-up E2E tests passing. 4 app smoke tests passing. Total: 26/26.

## TDD Process

- RED commit (`330080a`): new tests written and confirmed failing against old SVG structure
- GREEN commits: implementation brought all 22 tests to passing

## Deviations from Plan

### Auto-added: Eye preview SVG placeholder files

**Rule 2 - Missing critical functionality:** The tests (`test_preview_fetched_not_inline`) verify that preview buttons fetch real SVGs with >10 paths. Without `eye-1.svg`, `eye-2.svg`, `eye-3.svg` in `frontend/assets/svg/dressup/`, the fetch would 404 and the tests would fail.

- **Found during:** Task 1 implementation
- **Fix:** Created 3 placeholder eye SVGs (each >10 paths) as geometric approximations; real AI art will replace them when the Plan 01 pipeline runs
- **Files modified:** `frontend/assets/svg/dressup/eye-1.svg`, `eye-2.svg`, `eye-3.svg`
- **Commit:** `ceed984`

### Auto-added: mermaid.svg multi-use structure

**Rule 2 - Missing critical functionality:** The new JS code targets `active-hair`, `active-eyes`, `active-tail`, `active-acc` use elements by ID. The existing SVG only had `active-character`. Without updating the SVG, all `swapPart()` calls would silently no-op (element not found).

- **Found during:** Task 1 implementation
- **Fix:** Added 5 stacked use elements and eye-1/2/3 stubs directly to mermaid.svg as structural stubs; Plan 01's `assemble.py` will overwrite this with real AI-generated content
- **Files modified:** `frontend/assets/svg/mermaid.svg`
- **Commit:** `ceed984`

## Self-Check: PASSED

All 7 created/modified files found on disk. All 3 task commits verified in git log.

## Diagnostics

- **Tab structure:** `document.querySelectorAll('.tab-btn').length` — should return 5 (Hair, Eyes, Tail, Acc, Color+Undo)
- **Default active tab:** `document.querySelector('.tab-btn.active')?.textContent` — should be "Hair" (was previously Tail)
- **SVG use elements:** `document.querySelectorAll('use[id^="active-"]')` — should have 5 elements: active-tail, active-body, active-hair, active-eyes, active-acc
- **Part swap verification:** After clicking a variant button, check `use#active-{category}` href attribute changes while other `use` elements remain unchanged
- **Per-part recolor:** After applying recolor, only the source group for the active category should have filter applied

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_dressup.py -v` | 0 | ✅ pass (22/22) | ~8s |
| 2 | `uv run pytest tests/test_app.py -v` | 0 | ✅ pass (4/4) | ~3s |
| 3 | RED commit `330080a` confirmed failing | — | ✅ pass | manual |
| 4 | GREEN commits bring all tests passing | — | ✅ pass | manual |
