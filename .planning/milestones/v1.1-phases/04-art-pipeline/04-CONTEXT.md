# Phase 4: Art Pipeline - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Local Python scripts that generate kawaii mermaid SVG assets (coloring pages and dress-up parts) via OpenAI gpt-image-1 API and vtracer tracing. Developer runs scripts locally, output goes to frontend/assets/svg/ for static serving. No frontend changes -- just asset generation.

</domain>

<decisions>
## Implementation Decisions

### Art Style
- Chibi kawaii style: big head, small body, oversized eyes, minimal detail (Sanrio-like)
- Coloring pages: generate black-and-white outline art directly (not full-color traced to outlines)
- Dress-up parts: generate full-color with flat fills for easy recoloring via fill attribute swaps

### Consistency
- Cross-generation consistency is not critical -- minor style variation between pages/parts is acceptable
- No need for seed-based anchoring or manual curation workflow

### Asset Inventory
- 4 coloring pages replacing existing (ocean, castle, seahorse, coral themes in chibi kawaii style)
- 3 tails, 3 hair styles, 3 accessories (matching current v1.0 variant count)

### Variant Alignment
- Claude's Discretion: approach for spatial alignment of dress-up parts (base mermaid + edit API masks vs separate generation). Pick whatever is most reliable with gpt-image-1.

### SVG Structure
- Claude's Discretion: defs+use pattern vs separate SVG files per part. Pick what works best with vtracer output and existing frontend code (dressup.js uses setAttribute to swap <use> href).

### API Key
- OPENAI_API_KEY environment variable (standard Python pattern)

### Intermediate Artifacts
- Keep generated PNGs in a separate directory (e.g., assets/generated/png/) for debugging and re-tracing
- Only final SVGs go to frontend/assets/svg/

### Error Handling
- Auto-retry failed API calls 3 times with exponential backoff
- Skip already-generated assets on re-run (idempotent)

### Script Design
- Claude's Discretion: one orchestrator script vs separate scripts per stage. Pick what works best for a dev-facing tool with retry and re-run needs. trace.py already exists in src/mermaids/pipeline/.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mermaids/pipeline/trace.py`: vtracer wrapper with `trace_to_svg()` function. Supports binary (outline) and color modes. Resizes to 1024px max, has tuned params for clean SVG output.
- `frontend/assets/svg/mermaid.svg`: hand-crafted SVG with defs+use pattern. Tail variants at `<g id="tail-1">` etc., positioned at fixed coordinates (viewBox 400x700). Watercolor filter applied.
- `frontend/assets/svg/coloring/`: 4 existing coloring page SVGs (page-1-ocean.svg through page-4-coral.svg)

### Established Patterns
- Pipeline code lives in `src/mermaids/pipeline/` (Python module)
- vtracer + Pillow already in dependencies (pyproject.toml)
- OpenAI SDK not yet a dependency -- needs to be added
- Project uses `uv` for package management

### Integration Points
- Generated coloring SVGs replace files in `frontend/assets/svg/coloring/`
- Generated dress-up SVG replaces `frontend/assets/svg/mermaid.svg`
- `frontend/js/dressup.js` reads variant IDs from SVG defs and swaps via `<use>` href
- `frontend/js/coloring.js` loads SVG coloring pages by path

</code_context>

<specifics>
## Specific Ideas

No specific requirements -- open to standard approaches for the pipeline implementation.

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope.

</deferred>

---

*Phase: 04-art-pipeline*
*Context gathered: 2026-03-09*
