# Phase 8: Dress-Up Art Rework - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the current "each variant is a different full character" dress-up approach with a single unified base mermaid body that has independently swappable hair, eyes, tail, and accessory parts. The base body is static; parts layer on top via stacked `<use>` elements. Art generated via gpt-image-1 edit API with non-overlapping region masks. Fixes DEBT-03 (hair/tail overlap).

</domain>

<decisions>
## Implementation Decisions

### Part variety & count
- 4 categories: hair, eyes, tail, accessories (eyes are new; accessories stay)
- 3 variants per category = 12 total parts + 1 static base body
- 81 possible combinations (3^4)

### Part styles
- Hair: similar to current (wavy, pigtails, bob) -- regenerated for shared base alignment
- Eyes: big round, sparkle, sleepy (kawaii variety)
- Tails: similar to current (fish, ribbon, star) -- regenerated for shared base alignment
- Accessories: similar to current (tiara, garland, bubble wand) -- regenerated for shared base alignment

### SVG structure
- Stacked `<use>` elements, one per layer: tail (back) > body (static) > hair (mid) > eyes (front) > accessories (top)
- All variant groups in `<defs>`, each `<use>` swaps independently via `href`
- Extends existing defs+use pattern from current architecture

### Recoloring behavior
- Per-part recoloring: color swatch applies to whichever category tab is active
- Body/skin color is fixed (not recolorable) -- only hair, tail, eyes, accessories can be recolored
- Existing color palette (10 preset swatches) stays the same

### Art generation pipeline
- gpt-image-1 edit API with region masks (same approach, refined regions)
- Redesign mask bounding boxes so hair, eyes, tail, and accessory regions do not overlap (fixes DEBT-03)
- Eyes get a small face-region mask (new)
- Fully automated -- regenerate with refined prompts until parts align, no manual SVG editing
- Fresh start: delete old generated PNGs/SVGs, regenerate everything from scratch

### Category tabs & UI
- Tab order: Hair > Eyes > Tail > Acc > Color + Undo button
- Keep current icon-only layout (24x24 SVG icons, 60pt+ touch targets)
- New eye icon: simple oval eye shape with circle pupil
- Existing tab icons for hair, tail, acc, color, undo stay similar

### Claude's Discretion
- Celebration trigger threshold (how many categories explored before sparkle fires)
- Exact mask region coordinates for each category
- Eye tab icon SVG design details
- Accessory tab icon (may need refresh for the new category set)

</decisions>

<specifics>
## Specific Ideas

- Keep the spirit of current variant styles but regenerate everything for the shared base body
- Eye styles: big round (classic kawaii), sparkle (star-pupil), sleepy (half-closed dreamy)
- gpt-image-1 confirmed as best model -- only one supporting both high quality and mask-based editing

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/js/dressup.js`: swapPart(), recolorActivePart(), getRecolorableElements() -- core swap/recolor logic, needs refactoring from single-use to multi-use pattern
- `frontend/js/sparkle.js`: triggerCelebration() -- reusable as-is
- `frontend/js/touch.js`: initTouch() -- reusable as-is
- `src/mermaids/pipeline/edit.py`: create_region_mask(), edit_region(), generate_dressup_variants() -- mask generation and edit API, needs new region definitions and multi-layer output
- `src/mermaids/pipeline/assemble.py`: assemble_mermaid_svg() -- needs rework from single-use to multi-use SVG structure
- `src/mermaids/pipeline/prompts.py`: DRESSUP_BASE_PROMPT, DRESSUP_VARIANTS -- needs eye category added, region mask prompts refined

### Established Patterns
- defs+use SVG pattern for variant swapping (extending to multiple `<use>` elements)
- OpenAI edit API with RGBA masks for region-based variant generation
- vtracer for raster-to-SVG tracing (reuse for all new parts)
- Background path stripping in assembly (_is_background_path)
- Color heuristics: skip dark outlines, skin tones, near-white in recoloring

### Integration Points
- `frontend/js/app.js` renderDressUp(): loads mermaid.svg, wires tabs -- needs updated tab HTML for new categories
- `frontend/assets/svg/mermaid.svg`: assembled SVG file -- new multi-layer structure
- `frontend/assets/svg/dressup/`: individual part SVGs for preview thumbnails
- `assets/generated/`: pipeline output directory (PNGs and traced SVGs)

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope.

</deferred>

---

*Phase: 08-dress-up-art-rework*
*Context gathered: 2026-03-12*
