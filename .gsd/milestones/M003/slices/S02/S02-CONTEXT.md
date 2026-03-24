---
id: S02
milestone: M003
status: ready
---

# S02: Coloring Art Rework — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Fix the 4 coloring page SVGs so their outlines have no gaps, preventing flood fill from leaking through broken lines into adjacent regions.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

The current coloring pages have gaps in their traced outlines — thin or broken lines from the AI art create pixel-level discontinuities when rasterized to canvas. Flood fill leaks through these gaps, coloring far more than the intended region. This makes the coloring activity frustrating for a 6-year-old who taps inside a small region and watches the entire page flood. S01 fixes the dress-up art; S02 fixes the coloring art. S03 (Cleanup & Stability) depends on both being correct.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- **Post-process the 4 existing coloring page SVGs** (page-1-ocean, page-2-castle, page-3-seahorse, page-4-coral) to close gaps in their outlines. The traced SVGs have 8–18 filled paths each; gaps occur where vtracer's binary tracing misses thin or broken lines from the AI-generated PNGs.
- **Add a post-processing step to the art pipeline** (`trace.py` or a new module) that programmatically thickens/dilates stroke outlines or connects nearby path endpoints to eliminate gaps. This runs after vtracer tracing and before frontend deployment.
- **Redeploy fixed SVGs** to `frontend/assets/svg/coloring/` and to `assets/generated/svg/coloring/`.
- **Verify flood fill containment** — unit or E2E tests that confirm tapping inside a bounded region does NOT flood beyond that region's outline boundary.
- **Keep the 4 existing page designs** (ocean, castle, seahorse, coral) — no new scenes or compositions.

### Out of Scope

- Changing the coloring UX/interaction model (gallery → pick page → tap fill / drag brush → undo → back stays as-is).
- Adding new coloring pages beyond the existing 4.
- Regenerating the coloring page PNGs from scratch via OpenAI (the existing PNGs are the source; the fix is in post-processing the traced SVGs).
- Changes to `floodfill.js`, `coloring.js`, or the canvas/SVG overlay rendering logic.
- Brush tool changes (size, shape, behavior).
- Flood fill tolerance tuning (tolerance is currently 48; may be adjusted during execution if needed, but is not the primary fix strategy).

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- **Post-process, don't regenerate:** The fix is programmatic SVG post-processing (dilate strokes, close gaps), not re-generating AI art or re-prompting. The existing 4 PNG source files in `assets/generated/png/coloring/` are the input.
- **Binary tracing mode preserved:** Coloring pages use `simplify=True` (binary colormode) in `trace.py`. The post-processing step works on the binary-traced SVG output, not the tracing parameters themselves.
- **Visual fidelity:** The coloring pages must still look like clean black-and-white outline art suitable for a child to color. Post-processing should thicken lines just enough to close gaps — not turn thin elegant lines into chunky blobs.
- **1024×1024 canvas:** The rasterized canvas size is fixed at 1024×1024. Gap closure must be effective at this resolution.
- **Existing tests must pass:** 102 tests currently pass; the coloring tests in `test_coloring.py` and `test_floodfill_unit.py` are the primary safety net.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `assets/generated/png/coloring/page-{1..4}-*.png` — source AI-generated PNGs (input to tracing)
- `assets/generated/svg/coloring/page-{1..4}-*.svg` — current vtracer-traced SVGs with gaps
- `src/mermaids/pipeline/trace.py` → `trace_to_svg()` — existing tracing function (binary mode)
- `scripts/trace_all.py` → `trace_coloring_pages()` — batch tracing entry point
- `frontend/js/coloring.js` — flood fill + canvas logic (should NOT need changes)
- `frontend/js/floodfill.js` — scanline flood fill algorithm (should NOT need changes)

### Produces

- `frontend/assets/svg/coloring/page-{1..4}-*.svg` — fixed coloring page SVGs with closed outlines
- `assets/generated/svg/coloring/page-{1..4}-*.svg` — intermediate fixed SVGs
- New or updated pipeline module for SVG gap-closing post-processing (e.g., `src/mermaids/pipeline/postprocess.py` or additions to `trace.py`)
- Updated `scripts/trace_all.py` or `scripts/run_pipeline.py` to include the post-processing step
- Tests verifying flood fill containment on the fixed pages

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- **Post-processing technique** — Should gaps be closed by dilating the SVG path strokes (add a stroke attribute to widen the filled paths), by morphologically dilating the rasterized PNG before tracing, or by detecting and connecting nearby path endpoints in the SVG? — *Current thinking: the simplest approach is to add a `stroke` attribute (matching the fill color, e.g., black) with a small width (1–3px) to all paths in the traced SVG. This effectively thickens outlines without altering path geometry. If that's insufficient, morphological dilation on the PNG before tracing is the fallback.*
- **Per-page tuning** — Will one set of post-processing parameters work for all 4 pages, or will each page need individual tuning? — *Current thinking: try a single parameter set first; only per-page tune if results vary significantly.*
- **Flood fill tolerance interaction** — The current fill tolerance is 48 (quite high). After closing gaps, should tolerance be reduced to be more precise, or left as-is? — *Current thinking: leave at 48 unless the thicker outlines cause visible color bleeding into the black lines themselves.*
