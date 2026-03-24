---
estimated_steps: 5
estimated_files: 5
skills_used:
  - test
---

# T01: Wrap hair paths in `<g id="hair-group">` and target for hue-rotate

**Slice:** S01 — Dress-Up → Coloring Pipeline + Hair Path Fix
**Milestone:** M004

## Description

The dress-up hue-rotate recoloring currently applies `filter: hue-rotate(Xdeg)` to the entire root `<svg>` element, which shifts color on body, skin, tail, and eyes — not just hair. The 9 dress-up SVGs already have a `<clipPath id="hair-clip">` that clips hair geometry to the visible hair region (~y ≤ 310). Two paths in each SVG carry `clip-path="url(#hair-clip)"` — these are the hair paths.

The fix: wrap those 2 clipped paths in a `<g id="hair-group">` wrapper element, then change `dressup.js` to apply the hue-rotate filter to `#hair-group` instead of the root SVG. This isolates the color shift to hair only.

**Important context from KNOWLEDGE.md:** The recoloring uses `svg.style.filter = 'hue-rotate(Xdeg)'` — it does NOT modify individual `path[fill]` attributes. Tests should assert `element.style.filter.includes('hue-rotate')` on the `#hair-group` element.

## Steps

1. **Edit all 9 SVGs** (`frontend/assets/svg/dressup/mermaid-{1-9}.svg`): In each file, find the 2 `<path>` elements that have `clip-path="url(#hair-clip)"`. Wrap them in `<g id="hair-group">...</g>`, placed immediately after the closing `</defs>` tag. Do NOT change the clipPath definition or any other paths. The result should look like:
   ```xml
   </defs>
   <g id="hair-group">
     <path d="..." fill="..." transform="..." clip-path="url(#hair-clip)"/>
     <path d="..." fill="..." transform="..." clip-path="url(#hair-clip)"/>
   </g>
   <path d="..." fill="..." .../>  <!-- remaining non-hair paths -->
   ```

2. **Update `recolorActivePart()` in `frontend/js/dressup.js`**: Change from applying filter to the root SVG element to applying it to `#hair-group`:
   - Find: `const svgEl = container.querySelector("svg");` then `svgEl.style.filter = ...`
   - Replace with: `const hairGroup = container.querySelector("#hair-group");` then `hairGroup.style.filter = ...`
   - Keep the null check pattern — if `#hair-group` not found, no-op.

3. **Update `selectCharacter()` in `frontend/js/dressup.js`**: After swapping the SVG content, clear the filter on `#hair-group` (not root SVG). Also update the undo callback that restores the previous character's hue-rotate — it should apply to `#hair-group` in the restored SVG.

4. **Update the existing `test_color_swatch_recolors_paths` test** in `tests/test_dressup.py`: The current test checks `svg.style.filter` on the root SVG element. Update it to check the `#hair-group` element's filter instead. Add a new test `test_hue_rotate_targets_hair_group_not_root` that verifies: after recoloring, `#hair-group` has a hue-rotate filter AND the root `<svg>` does NOT have a filter.

5. **Run all existing dress-up tests** to confirm no regressions. The undo tests check filter state — they need to pass with the new targeting.

## Must-Haves

- [ ] All 9 `mermaid-{1-9}.svg` files have `<g id="hair-group">` wrapping exactly the 2 clipped hair paths
- [ ] `dressup.js` `recolorActivePart()` applies hue-rotate to `#hair-group`, not root SVG
- [ ] `dressup.js` `selectCharacter()` clears filter on `#hair-group`, not root SVG
- [ ] Undo for character swap restores hue-rotate on `#hair-group` in the restored SVG
- [ ] Test verifies hue-rotate targets `#hair-group` and root SVG has no filter
- [ ] All existing dress-up tests pass

## Verification

- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_dressup.py -x -q` — all tests pass including new hair-group test
- `grep -c 'id="hair-group"' frontend/assets/svg/dressup/mermaid-1.svg` returns 1
- `grep -c 'id="hair-group"' frontend/assets/svg/dressup/mermaid-9.svg` returns 1
- `grep -q '#hair-group' frontend/js/dressup.js` — dressup.js references `#hair-group`

## Inputs

- `frontend/assets/svg/dressup/mermaid-1.svg` — representative SVG showing the 2 clipped hair paths and clipPath definition
- `frontend/assets/svg/dressup/mermaid-2.svg` — second SVG to confirm same structure
- `frontend/js/dressup.js` — current recoloring and character swap logic
- `tests/test_dressup.py` — existing tests, especially `test_color_swatch_recolors_paths` and undo tests

## Expected Output

- `frontend/assets/svg/dressup/mermaid-1.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-2.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-3.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-4.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-5.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-6.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-7.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-8.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/assets/svg/dressup/mermaid-9.svg` — updated with `<g id="hair-group">` wrapper
- `frontend/js/dressup.js` — hue-rotate targets `#hair-group`
- `tests/test_dressup.py` — updated and new tests for hair-group targeting
