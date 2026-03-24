---
id: S01
milestone: M003
status: in_progress
---

# S01: Dress Up Art Rework — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Fix the dress-up recoloring so tapping a color swatch changes only the hair — not the entire mermaid — by grouping and clipping SVG paths per body-part category across all 9 characters.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

The current `hue-rotate` filter is applied to the whole `<svg>`, shifting every path's color at once (hair, skin, tail, eyes). Hair paths traced by vtracer span y 59–1000+, extending far behind the body and tail. This makes recoloring unusable — a 6-year-old taps "blue" expecting blue hair and gets a blue-tinted everything. Fixing this unblocks S02 (Coloring Art Rework) which depends on the dress-up art pipeline being correct, and unblocks S03 (Cleanup & Stability) downstream.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- **Manually tag paths** in all 9 mermaid SVGs (`mermaid-1` through `mermaid-9`) to identify which paths belong to which body-part category (hair, eyes, tail, accessories). Typically 1–2 hair paths per character, plus paths for each other category.
- **Group all 4 categories** by wrapping identified paths in `<g>` elements with semantic IDs (e.g. `id="hair-group"`, `id="eyes-group"`, `id="tail-group"`, `id="acc-group"`). This is a one-time structural investment that enables per-part recoloring now and in the future.
- **Clip hair paths** to the visible hair zone (~y 0–300) using SVG `<clipPath>`. Hair paths currently span y 59–1000+ behind the body. Clipping removes the hidden-behind-body portion as a belt-and-suspenders defense alongside targeted recoloring.
- **Change recoloring to hair-group only**: modify `dressup.js` → `recolorActivePart()` to apply `hue-rotate` to the `<g id="hair-group">` element instead of the root `<svg>`.
- **Update `mermaid.svg`** (the default character) to match the updated `mermaid-1.svg`.
- **Update tests** to verify hair-only recoloring: `svg.style.filter` should be empty; `hair-group.style.filter` should have the `hue-rotate` value.
- **Update `assemble_combo_svg()`** in `assemble.py` if the new SVG structure (groups, clipPaths) requires assembly changes.

### Out of Scope

- Per-part recoloring UI for tail/eyes/accessories (groups are created now but only hair recoloring is wired in the frontend).
- Generating new art or changing the 9 character designs.
- Multi-layer part-swapping architecture (the gallery approach stays).
- Tab-based UI for part selection (future slice).
- Changing the SVG `viewBox` or canvas size.

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- **D001 (locked):** Hair paths must be clipped to ~y 0–290, aligned with `REGIONS["hair"]` in `edit.py`.
- **Manual path tagging:** Each character has a unique path structure (different number of paths, different fills). There is no automated way to reliably identify hair vs. skin — manual inspection per character is required.
- **hue-rotate on hair group:** Preserves color variation within hair (highlights, shadows) while shifting the overall hue. Direct fill replacement was rejected because it flattens hair to a single color.
- **Visual fidelity at rest:** With no recoloring applied, all 9 characters must render identically to their current appearance. Grouping and clipping must not alter the default visual.
- **102 existing tests must pass:** The test suite is the safety net; no regressions allowed.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `frontend/assets/svg/dressup/mermaid-{1..9}.svg` — current flat-path SVGs to be restructured
- `src/mermaids/pipeline/edit.py` → `REGIONS["hair"]` = `(150, 0, 874, 290)` — defines the hair clip boundary
- `frontend/js/dressup.js` → `recolorActivePart()` — current whole-SVG hue-rotate logic to be changed
- `src/mermaids/pipeline/assemble.py` → `assemble_combo_svg()` — may need updates for group/clip structure

### Produces

- `frontend/assets/svg/dressup/mermaid-{1..9}.svg` — restructured with `<g>` groups for hair, eyes, tail, acc and `<clipPath>` on hair
- `frontend/assets/svg/mermaid.svg` — updated default (copy of restructured mermaid-1)
- Updated `frontend/js/dressup.js` — `recolorActivePart()` targets `#hair-group` instead of root SVG
- Updated `tests/test_dressup.py` — recolor assertions check `hair-group.style.filter` not `svg.style.filter`

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- **Body/untagged paths** — After tagging hair, eyes, tail, and accessories, the remaining paths are the body/skin and face. Should these be wrapped in a `<g id="body-group">` for completeness, or left as ungrouped direct children of `<svg>`? — *Current thinking: wrap in `body-group` for structural consistency, even though body recoloring is out of scope.*
- **Background rectangle paths** — Some characters (mermaid-2, mermaid-8) have a full-canvas background path (y 0–1024, near-white fill). These were supposed to be stripped by `assemble_combo_svg()` but may still be present. Should they be removed during this restructuring? — *Current thinking: yes, strip them if found.*
- **Clip boundary precision** — `REGIONS["hair"]` defines y 0–290, but some hairstyles extend to y ~320 (e.g. long braids). Should the clip boundary be slightly generous (~y 320) to avoid cutting visible hair, or strictly match the REGIONS definition? — *Current thinking: use a generous clip (~y 320) and update REGIONS to match if needed.*
