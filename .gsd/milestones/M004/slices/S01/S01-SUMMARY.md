# S01 Summary: Dress-Up → Coloring Pipeline + Hair Path Fix

**Milestone:** M004  
**Status:** Complete  
**Tests:** 111 passing (was 104 before this slice; +7 new)

## What This Slice Delivered

Three capabilities wired together into one creative flow:

1. **Hair hue-rotate isolation (HAIR-01):** All 9 dress-up SVGs + `mermaid.svg` now wrap the 2 clipped hair paths in `<g id="hair-group">`. `dressup.js` applies `filter: hue-rotate(Xdeg)` to `#hair-group` only, not the root SVG. Changing hair color no longer shifts body/skin/tail colors.

2. **9 coloring outline assets (PIPE-03):** B&W placeholder SVGs deployed to `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg`. Each is a distinct chibi-mermaid shape (3,200–3,500 bytes) with `fill="white" stroke="#000"` closed shapes — valid flood-fill targets. A generation script (`scripts/generate_dressup_outlines.py`) supports `--placeholder` (what shipped), `--dry-run`, and full AI pipeline modes.

3. **"Color This!" button + routing (PIPE-01, PIPE-02):** A coral gradient button in dress-up navigates to `#/coloring?character=mermaid-N`. Router parses the `?character=` query param. `renderColoringForCharacter()` loads the matching outline SVG on the coloring canvas. Back button returns to `#/dressup`.

## Key Decisions Made

- **Hair-group wrapper approach:** Instead of clipping hair paths geometrically or redrawing them, wrapped existing clipped paths in `<g id="hair-group">` and moved the CSS filter target from root SVG to the group. Simpler, non-destructive, preserves existing clipPath geometry.
- **Placeholder SVGs over blank stubs:** Without OPENAI_API_KEY, created distinct geometric mermaid shapes per character (not identical placeholders). Functional for the pipeline — flood-fill works, canvas loads them — but not character-faithful. Re-runnable with API key later.
- **Standalone renderColoringForCharacter():** Duplicates the `openColoringPage` pattern rather than sharing code, keeping gallery coloring and dress-up coloring flows cleanly separated.

## Files Changed (key)

| Area | Files |
|------|-------|
| SVG assets | `frontend/assets/svg/dressup/mermaid-{1-9}.svg`, `frontend/assets/svg/mermaid.svg` (hair-group wrapper) |
| Outline assets | `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` (new) |
| Frontend JS | `frontend/js/app.js` (button, router, renderColoringForCharacter), `frontend/js/dressup.js` (hair-group targeting) |
| CSS | `frontend/css/style.css` (.color-this-btn) |
| Scripts | `scripts/generate_dressup_outlines.py` (new) |
| Tests | `tests/test_dressup.py` (+2), `tests/test_pipeline.py` (+2), `tests/test_e2e.py` (+4) |

## Patterns Established

- **Hair-group filter pattern:** `container.querySelector('#hair-group').style.filter = 'hue-rotate(Xdeg)'` — query inside the SVG container, not the root SVG element. Null guard prevents silent no-op if SVG lacks the group.
- **Hash-with-query-params routing:** `rawHash.split('?')` → `[route, queryString]`, then parse `key=value` pairs. No URLSearchParams — compatible with the existing hash-based SPA router.
- **SVG XML comment safety:** No `--` (double hyphen) or non-ASCII in SVG comments. Chromium's strict XML parser silently rejects via `img.onerror` with no useful error message.
- **Test pattern for hair isolation:** `hairGroup.style.filter.includes('hue-rotate')` AND `svg.style.filter === ''` — asserts filter is on the group, not leaking to root.

## What the Next Slice Should Know

- **Outline assets are placeholders:** The 9 `dressup-coloring/*.svg` files work functionally (load on canvas, accept flood-fill) but are geometric shapes, not AI-generated character-faithful outlines. Run `python scripts/generate_dressup_outlines.py` with `OPENAI_API_KEY` to replace them.
- **mermaid.svg is a separate file from dressup/mermaid-1.svg:** Both need identical structural changes (hair-group, etc.). The initial dress-up display uses `mermaid.svg`; character swap loads `dressup/mermaid-N.svg`.
- **111 tests passing:** Full suite covers dress-up (15), pipeline (7), E2E (14), and other suites. No flaky tests observed.
- **Remaining M004 slices are standalone:** S02 (icons) and S03 (coloring pages 5-9) have no dependency on S01's work.

## Risks Retired

- ✅ **Hair path fix risk:** Hue-rotate isolation confirmed working via E2E test (`test_hue_rotate_targets_hair_group_not_root`).
- ✅ **Pipeline integration risk:** Full dress-up → coloring flow confirmed via 4 E2E tests (button visibility, navigation with default/selected character, back button).
- ⚠️ **AI outline quality risk:** Partially retired — pipeline infrastructure works, but actual AI-generated outlines deferred until API key available. Placeholder art proves the flow works end-to-end.

## Requirements Status

| Requirement | Status After S01 |
|------------|-----------------|
| PIPE-01 | Validated — E2E test confirms dress-up → coloring navigation |
| PIPE-02 | Validated — "Color This!" button visible and functional |
| PIPE-03 | Validated (partial) — 9 outlines exist and load; placeholders not character-faithful |
| HAIR-01 | Validated — hue-rotate targets #hair-group only, E2E test confirms |
