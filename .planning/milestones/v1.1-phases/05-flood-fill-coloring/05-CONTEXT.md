# Phase 5: Flood-Fill Coloring - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the existing SVG region-based coloring (data-region tap-to-fill) with canvas-based flood fill and SVG line art overlay. Child taps white areas on a coloring page to fill with color, with undo support. No new pages, no new UI activities -- just upgrading the coloring interaction mechanism.

</domain>

<decisions>
## Implementation Decisions

### Fill Interaction
- Tapping any region (white or already colored) fills it with the currently selected color -- overwrite is allowed
- Attempt a quick spread animation (~200ms) where color visibly spreads outward from the tap point
- If the spread animation causes performance issues on iPad, fall back to instant fill -- performance wins over animation
- Undo button should be visually disabled (grayed out) when the undo stack is empty

### Color Palette
- Keep the existing 10 preset color swatches (ocean teal, lavender, hot pink, gold, sky blue, pale green, tomato red, plum, light salmon, turquoise)
- Same palette as dress-up -- consistency across activities

### Claude's Discretion
- Fill visual feedback (sparkle, opacity pulse, or none) -- pick what feels delightful without slowing interaction
- Swatch layout (bottom panel vs side panel) -- pick best layout for iPad landscape/portrait
- Selected color indicator styling
- Undo depth (30 cap vs unlimited) -- balance iPad memory constraints with usability
- Whether to include a "clear all" reset button alongside undo
- Progress persistence when navigating back to gallery (lost vs preserved in session)
- Gallery thumbnail indicators for colored pages
- Navigation warning when switching to dress-up (no warning vs gentle hint) -- audience is a 6-year-old

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/js/coloring.js`: State management module with COLORS array, undo stack (closure-based, MAX_UNDO=30), fillRegion(), undo(), setSelectedColor(). Needs rewrite for canvas-based approach but structure is reusable.
- `frontend/js/sparkle.js`: triggerSparkle() for tap feedback -- can be reused on canvas tap events
- `frontend/js/touch.js`: pointerdown event delegation on SVG with sparkle + opacity pulse. Pattern can inform canvas tap handling.
- `frontend/js/app.js`: openColoringPage() loads SVG, wires color swatches, back/undo buttons, and pointerdown region fill. This function needs significant rework for canvas+SVG hybrid.

### Established Patterns
- Pointer event delegation via pointerdown (not click) -- touch-friendly
- Hash-based SPA router in app.js -- coloring route renders gallery, page selection opens coloring view
- Undo uses closure stack pattern (pushUndo with function capture)
- Color swatches rendered as buttons with data-color attribute and .selected class

### Integration Points
- `openColoringPage()` in app.js is the main entry point -- needs to set up canvas + SVG overlay instead of just SVG
- Gallery thumbnail rendering in `renderColoring()` stays mostly the same
- COLORING_PAGES metadata array (id, label, file path) remains the source of truth
- Canvas needs to be released when navigating away (hashchange or back button) per iPad Safari memory decision in STATE.md

</code_context>

<specifics>
## Specific Ideas

No specific requirements -- open to standard approaches for canvas flood fill implementation.

</specifics>

<deferred>
## Deferred Ideas

- Rainbow color swatch with color picker (full color wheel / custom color selection) -- future phase or v2 feature

</deferred>

---

*Phase: 05-flood-fill-coloring*
*Context gathered: 2026-03-09*
