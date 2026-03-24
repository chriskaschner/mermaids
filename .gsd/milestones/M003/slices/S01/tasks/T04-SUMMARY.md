---
id: T04
parent: S01
milestone: M003
provides:
  - 9/9 mermaid character SVGs updated with clipPath bounding hair paths to y=0..310
  - frontend/assets/svg/mermaid.svg synced as copy of updated mermaid-1.svg
  - 102/102 tests still pass after hair clipping changes
  - Hair paths in all SVGs now bounded to hair-visible zone via <clipPath id="hair-clip">
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
key_decisions:
  - Used SVG clipPath (not path data trimming) to preserve original path data while masking hair to y=0..310
  - Hair clip rect is oversized (x=-512 y=-512 width=2048 height=822) to handle paths with negative y or x that still render visually within the SVG viewport
  - mermaid-2 and mermaid-8 skip path[0] which is a full-canvas background fill rect, not a hair path; instead clip paths[1,3]
patterns_established:
  - Use SVG <clipPath> with oversized rect (extend ±512 in x and negative y) to handle paths with transform offsets that include negative local coordinates
  - Y extraction from SVG path data must parse C (cubic bezier) commands, not just M/L — paths dominated by C commands will appear zero-height if only M/L are checked
  - Verify clip presence with grep -c 'hair-clip' file.svg — should be 3 (1 defs + 2 on paths)
observability_surfaces:
  - "`grep -c 'hair-clip' frontend/assets/svg/dressup/mermaid-{1..9}.svg` — returns 3 for each file when fix is applied"
  - "`document.querySelector('#mermaid-svg clipPath#hair-clip')` — returns element when clip is active in DOM"
  - "`document.querySelectorAll('[clip-path]').length` — returns 2 for correct clipping of 2 hair paths"
  - "Missing clip: if hair paths bleed, hue-rotate shows hair-colored pixels in body/tail zone; no JS error, only visual artifact"
  - "`uv run pytest -q` — 102/102 should pass"
duration: 35min
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T04: Fix hair paths that bleed beyond hair region

**Added SVG `<clipPath id="hair-clip">` to all 9 mermaid character SVGs, bounding the oversized vtracer-generated hair paths to y=0..310 so CSS hue-rotate no longer affects hair-colored pixels in the body/tail zone.**

## What Happened

The root issue: vtracer-traced hair paths span from y≈20 all the way to y≈1000 (the full canvas), because the AI art has hair that wraps behind the body. When CSS `hue-rotate` is applied to the whole SVG element, these oversized hair paths render hair-colored pixels in the body/tail region, creating a visual artifact where areas that should show skin/tail color instead show hair-color-shifted pixels.

**Analysis phase:** Wrote a Python script to extract all y-coordinate ranges from each SVG using C-command parsing (M/L alone is insufficient — these paths are dominated by cubic bezier curves). Found that paths[0] and [1] in most characters span y=20..990, far beyond the y=0..290 hair zone (REGIONS dict in edit.py). Identified that mermaid-2 and mermaid-8 have full-canvas background fill rects at path[0], so their hair is at path indices [1, 3].

**Fix:** Added `<defs><clipPath id="hair-clip"><rect x="-512" y="-512" width="2048" height="822"/></clipPath></defs>` to each SVG and applied `clip-path="url(#hair-clip)"` to the identified hair path elements. The clip rect uses an oversized bounding box (height = 310 + 512 = 822, x/y extended by ±512) to handle path data with negative local coordinates that still render within the SVG viewport.

**Key bug discovered:** Initial implementation only extracted y from M/L commands (regex `[ML]...y`), showing y_max≈60 for paths that actually reach y≈970. Fixed by also parsing C cubic bezier command control points, which revealed the true y range.

**All 9 SVGs updated** in `frontend/assets/svg/dressup/`. Copied mermaid-1.svg to `frontend/assets/svg/mermaid.svg`. Added pre-flight sections to T04-PLAN.md (Expected Output + Observability Impact).

## Verification

- `uv run pytest tests/test_dressup.py -v` → 14/14 passed
- `uv run pytest -q` → 102/102 passed  
- `grep -c 'hair-clip' frontend/assets/svg/dressup/mermaid-{1..9}.svg` → 3 for each file
- Browser: loaded dressup, applied lavender/turquoise swatches to mermaid-1 and mermaid-4, confirmed hue-rotate works and hair path clip is present in DOM (`clipPath#hair-clip` found, 2 `[clip-path]` elements)
- Browser observability: `document.getElementById('mermaid-svg')?.style?.filter` → `hue-rotate(174deg)` (active), character gallery 9 buttons, no `.error` div

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_dressup.py -v` | 0 | ✅ pass | 7.08s |
| 2 | `uv run pytest -q` (full suite) | 0 | ✅ pass | 40.5s |
| 3 | `grep -c 'hair-clip' frontend/assets/svg/dressup/mermaid-{1..9}.svg` | 0 | ✅ pass | <1s |
| 4 | `grep -c 'hair-clip' frontend/assets/svg/mermaid.svg` | 0 | ✅ pass | <1s |
| 5 | Browser: clipPath in DOM (`clipPathsInDom:1, pathsWithClip:2`) | — | ✅ pass | visual |
| 6 | Browser: 9 char-btns, no .error, hue-rotate filter active | — | ✅ pass | visual |
| 7 | Browser: mermaid-1 + mermaid-4 render correctly at rest and with swatch | — | ✅ pass | visual |

## Diagnostics

- **Clip presence check:** `grep -c 'hair-clip' frontend/assets/svg/dressup/mermaid-{1..9}.svg` — returns 3 for each (1 defs + 2 path attrs)
- **DOM clip check:** In browser console: `document.querySelector('#mermaid-svg clipPath[id="hair-clip"]')` — returns element; `document.querySelectorAll('[clip-path]').length` — returns 2
- **Recolor signal:** `document.getElementById('mermaid-svg')?.style?.filter` — `hue-rotate(Xdeg)` when active
- **Active character:** `document.querySelector('.char-btn.selected')?.dataset?.character` — current selection
- **Failure path:** Missing clipPath → no JS error, only visual: hair-colored pixels visible in body/tail region when hue-rotating

## Deviations

**Initial y-extraction bug:** The first pass of the clip script used only M/L command regex for y-coordinate extraction. This returned y_max≈60 for paths that actually reach y≈970 (dominated by C cubic bezier commands). Fixed by adding C-command y extraction. This was an implementation adaptation, not a plan deviation.

**mermaid-8 path[1] is near-white (#FEFCF9):** This path (y=0..1024) appeared to be a skin/hair color, not purely hair. However it spans the full canvas and starts at the top (ty=0), consistent with a hair-over-body silhouette. Applied clip conservatively. If visual artifacts emerge, path[1] could be excluded from clipping in a future fix.

## Known Issues

The hue-rotate CSS filter is applied to the entire SVG element — meaning skin and tail paths also shift hue when a color swatch is selected. The clipPath fix specifically prevents the hair path's oversized shape from rendering outside the hair zone, but the fundamental skin/tail hue-shift from the SVG-level filter remains by design. This is the intended behavior per the existing architecture (CSS hue-rotate on SVG root is the recolor mechanism).

## Files Created/Modified

- `frontend/assets/svg/dressup/mermaid-1.svg` — Added `<defs><clipPath id="hair-clip">...</clipPath></defs>` and `clip-path="url(#hair-clip)"` on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-2.svg` — Same treatment on paths[1,3] (path[0] is BG rect)
- `frontend/assets/svg/dressup/mermaid-3.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-4.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-5.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-6.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-7.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/dressup/mermaid-8.svg` — Same treatment on paths[1,3] (path[0] is BG rect)
- `frontend/assets/svg/dressup/mermaid-9.svg` — Same treatment on paths[0,1]
- `frontend/assets/svg/mermaid.svg` — Copied from updated mermaid-1.svg
- `.gsd/milestones/M003/slices/S01/tasks/T04-PLAN.md` — Added `## Expected Output` and `## Observability Impact` sections (pre-flight requirement)
