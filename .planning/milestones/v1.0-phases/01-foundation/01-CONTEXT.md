# Phase 1: Foundation - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the SVG rendering pipeline, art asset workflow, touch interaction system, and navigation shell -- all running in iPad Safari. A child can see a watercolor-styled mermaid, tap regions and get sparkle feedback, and navigate between activity screens. Dress-up customization and coloring are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Art asset pipeline
- Generate watercolor mermaid art using AI image tools, then trace/convert raster images to SVG
- Tool selection is flexible -- try multiple AI tools (Midjourney, DALL-E, Claude, etc.) and pick what produces the best results
- For Phase 1, create a simple mermaid silhouette divided into tappable regions (tail, hair, body) -- proves the SVG + touch pipeline works without needing final art
- Detailed, polished art and swappable parts are Phase 2 concerns -- Phase 1 validates the pipeline

### Touch feedback
- Sparkle/shimmer particle effect on tapped regions, fading after ~0.5s
- Very forgiving tap detection: expand hit areas beyond visible SVG boundaries, snap to nearest region for imprecise child taps
- All interactive elements maintain 60pt+ tap targets per FOUN-01

### Claude's Discretion
- Watercolor art style direction (balance 6-year-old appeal with what traces cleanly to SVG)
- Whether background taps produce subtle feedback (e.g., water ripple) or only mermaid regions respond
- Sparkle color approach (consistent gold/white vs region-matched colors)
- Home screen layout and navigation icon placement (not discussed -- standard approaches fine)
- SVG tracing tool selection and optimization

</decisions>

<specifics>
## Specific Ideas

- Inspired by Crayola Create and Play -- zero-friction creative play for a 6-year-old
- "Dreamy watercolor mermaid aesthetic" is the north star for all visuals
- Phase 1 mermaid can be a simplified proof-of-concept; beautiful final art comes with Phase 2

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- None -- greenfield project, no code exists yet

### Established Patterns
- Vanilla JS + FastAPI decided at project level (no framework, no build step)
- SVG-first rendering for all interactive content

### Integration Points
- SVG touch event handling must work reliably in iPad Safari
- Art asset pipeline (AI image -> SVG trace) needs early prototyping -- flagged as biggest risk

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-09*
