# Phase 6: Dress-Up Art Swap - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the hand-crafted mermaid SVG with AI-generated kawaii art and make the existing dress-up interaction (variant swapping + color recoloring) work with the new assets. No new activities, no new categories, no new UI -- just swapping the art and ensuring the defs+use mechanism functions correctly.

</domain>

<decisions>
## Implementation Decisions

### Recoloring behavior
- Uniform recolor: apply selected swatch color to ALL fill-bearing elements (current behavior preserved)
- Skip elements with fill="none" -- outlines/strokes keep their original color for kawaii line-art look
- Per-variant color memory: each variant remembers its own color override (state.colors[variantId]) -- switching variants restores their individual colors

### Body/face cohesion
- Claude's Discretion: evaluate visual match between hardcoded body/face and AI-generated kawaii parts, decide whether to keep or regenerate
- If regeneration needed, OK to make extra OpenAI API calls for body art
- Face and body always stay fixed skin tone -- NOT recolorable. Only tail, hair, and accessories are recolorable categories

### Variant preview icons
- Use scaled-down actual traced SVGs as preview thumbnails (not hardcoded simplified icons)
- Fetch variant SVGs from files at runtime (e.g., fetch dressup/tail-1.svg) rather than inlining in JS
- Preview button size: 48x48px (up from 24x24) -- meets 60pt+ touch target guideline for iPad
- Previews reflect applied color overrides: if user recolors tail-1 pink, its thumbnail also shows pink

### Claude's Discretion
- Whether AI-generated SVGs need regeneration/tuning for clean recoloring (evaluate and decide)
- Body/face approach: keep hardcoded or regenerate to match kawaii style (based on visual evaluation)
- Any CSS/layout adjustments needed for larger preview buttons in the options row

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/generated/svg/dressup/`: 9 traced variant SVGs (tail-1..3, hair-1..3, acc-1..3) ready from Phase 4
- `assets/generated/svg/mermaid.svg`: assembled SVG with defs+use structure from Phase 4 pipeline
- `src/mermaids/pipeline/assemble.py`: builds mermaid.svg with defs+use, hardcoded body/face, scale transforms
- `frontend/js/dressup.js`: PARTS map, swapPart(), recolorActivePart(), state management, undo stack
- `frontend/js/app.js`: renderDressUp() fetches /assets/svg/mermaid.svg, wires tabs and options

### Established Patterns
- defs+use variant swap: `<use>` href points to variant `<g>` in `<defs>`, swapped via setAttribute
- Recoloring: `applyColorToSource()` sets fill on all path/circle/ellipse/rect children with fill != "none"
- Original colors captured lazily on first recolor for undo support (originalColorsMap)
- Pointer event delegation via pointerdown (touch-friendly)
- Hash-based SPA router in app.js

### Integration Points
- `frontend/assets/svg/mermaid.svg` -- needs replacing with assembled kawaii version
- `frontend/assets/svg/dressup/` -- new directory for individual variant SVGs (for preview thumbnails)
- `getVariantPreviewSVG()` in dressup.js -- needs rewrite to fetch real SVGs instead of returning inline strings
- `renderOptions()` in dressup.js -- needs update for 48x48 buttons and color-reflecting previews
- `assemble.py copy_mermaid_to_frontend()` -- deploys assembled SVG to frontend

</code_context>

<specifics>
## Specific Ideas

No specific requirements -- open to standard approaches for the art swap and preview implementation.

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope.

</deferred>

---

*Phase: 06-dress-up-art-swap*
*Context gathered: 2026-03-09*
