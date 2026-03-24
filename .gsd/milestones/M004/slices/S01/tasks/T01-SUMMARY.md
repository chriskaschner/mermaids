---
id: T01
parent: S01
milestone: M004
provides:
  - hair-group wrapper in all 9 dressup SVGs + mermaid.svg
  - dressup.js recoloring targets #hair-group instead of root SVG
  - test verifying hue-rotate isolation to hair only
key_files:
  - frontend/assets/svg/dressup/mermaid-1.svg
  - frontend/assets/svg/dressup/mermaid-2.svg
  - frontend/assets/svg/dressup/mermaid-3.svg
  - frontend/assets/svg/dressup/mermaid-4.svg
  - frontend/assets/svg/dressup/mermaid-5.svg
  - frontend/assets/svg/dressup/mermaid-6.svg
  - frontend/assets/svg/dressup/mermaid-7.svg
  - frontend/assets/svg/dressup/mermaid-8.svg
  - frontend/assets/svg/dressup/mermaid-9.svg
  - frontend/assets/svg/mermaid.svg
  - frontend/js/dressup.js
  - tests/test_dressup.py
key_decisions:
  - Wrapped the 2 hair paths (clip-path="url(#hair-clip)") in <g id="hair-group"> for all 9 dressup SVGs plus mermaid.svg (initial dress-up SVG)
  - Some SVGs (mermaid-2, mermaid-8) had non-hair paths between the two hair paths; fixed by extracting only the 2 hair paths into the group using a two-pass approach
patterns_established:
  - Python script to add hair-group wrapper: find indices of clip-path="url(#hair-clip)" lines, insert wrapper; then verify no non-hair paths captured inside
  - Test pattern: evaluate JS in browser, check hairGroup.style.filter includes 'hue-rotate' AND svg.style.filter is empty
observability_surfaces:
  - Browser DevTools → select #hair-group element → check Styles panel for filter property
  - If #hair-group is missing from DOM, recolorActivePart() silently no-ops (null guard)
duration: ~45m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T01: Wrap hair paths in `<g id="hair-group">` and target for hue-rotate

**Added `<g id="hair-group">` wrapper to all 10 dress-up SVGs and updated dressup.js to apply hue-rotate only to hair paths, isolating color shift from body/skin/tail.**

## What Happened

The dress-up hue-rotate was applying `filter: hue-rotate(Xdeg)` to the root `<svg>` element, shifting all colors (body, skin, tail, eyes). The fix wraps the 2 clipped hair paths in `<g id="hair-group">` and retargets the filter to that group.

**SVG edits (10 files):** Each SVG has exactly 2 `<path>` elements with `clip-path="url(#hair-clip)"`. A Python script found the line indices for those 2 paths and inserted `<g id="hair-group">` wrapper tags around them. Two SVGs (mermaid-2, mermaid-8) had a non-hair path between the two hair paths — a second pass detected and fixed these by extracting only the 2 hair paths into a clean group. Also updated `mermaid.svg` (the initial dress-up display SVG, separate from `dressup/mermaid-1.svg`) with the same wrapper.

**dressup.js edits:**
- `recolorActivePart()`: `container.querySelector("#hair-group")` replaces `container.querySelector("svg")`; null guard preserved
- `selectCharacter()`: clears filter on `#hair-group` after SVG swap; undo callback restores hue-rotate on `#hair-group` in the restored SVG

**tests/test_dressup.py edits:**
- `test_color_swatch_recolors_paths`: updated to check `hairGroup.style.filter` (not `svg.style.filter`)
- `test_undo_reverts_color`: updated to read/verify `hairGroup.style.filter`
- Added `test_hue_rotate_targets_hair_group_not_root`: asserts `#hair-group` has hue-rotate filter AND root SVG has empty filter

## Verification

Ran `pytest tests/test_dressup.py -x -q` — 15 tests passed (13 original + 2 new).

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `.venv/bin/python -m pytest tests/test_dressup.py -x -q` | 0 | ✅ pass | 8.0s |
| 2 | `grep -c 'id="hair-group"' frontend/assets/svg/dressup/mermaid-1.svg` | 0 (returns 1) | ✅ pass | <1s |
| 3 | `grep -c 'id="hair-group"' frontend/assets/svg/dressup/mermaid-9.svg` | 0 (returns 1) | ✅ pass | <1s |
| 4 | `grep -q '#hair-group' frontend/js/dressup.js` | 0 | ✅ pass | <1s |

## Diagnostics

- Browser DevTools → Elements → select `#hair-group` → Styles panel shows the active `filter: hue-rotate(Xdeg)` value
- Network tab: `mermaid-N.svg` request should show 200 with SVG content containing `id="hair-group"`
- If clicking a color swatch has no visible effect, check: `document.querySelector('.mermaid-container #hair-group')` in console — if null, SVG loaded without the group (stale cache or wrong file)

## Deviations

**mermaid.svg must also be updated:** The plan only mentioned the 9 `dressup/mermaid-N.svg` files, but the dress-up screen initially renders `assets/svg/mermaid.svg` (not mermaid-1.svg). Without the group in mermaid.svg, recoloring silently no-ops on the initial state. Fixed by applying the same wrapper to `mermaid.svg`.

**Non-consecutive hair paths (mermaid-2, mermaid-8):** The plan assumed the 2 hair paths were always consecutive lines. Two SVGs had a non-hair body path between them. Fixed with a two-pass script that detects and removes non-hair paths from inside the group (extracting just the 2 hair paths).

## Known Issues

None.

## Files Created/Modified

- `frontend/assets/svg/dressup/mermaid-1.svg` — added `<g id="hair-group">` wrapper around 2 hair paths
- `frontend/assets/svg/dressup/mermaid-2.svg` — same (non-consecutive case fixed)
- `frontend/assets/svg/dressup/mermaid-3.svg` — same
- `frontend/assets/svg/dressup/mermaid-4.svg` — same
- `frontend/assets/svg/dressup/mermaid-5.svg` — same
- `frontend/assets/svg/dressup/mermaid-6.svg` — same
- `frontend/assets/svg/dressup/mermaid-7.svg` — same
- `frontend/assets/svg/dressup/mermaid-8.svg` — same (non-consecutive case fixed)
- `frontend/assets/svg/dressup/mermaid-9.svg` — same
- `frontend/assets/svg/mermaid.svg` — same (initial dress-up SVG, not in original plan)
- `frontend/js/dressup.js` — recolorActivePart(), selectCharacter(), undo callback all retargeted to #hair-group
- `tests/test_dressup.py` — updated 2 tests + added test_hue_rotate_targets_hair_group_not_root
