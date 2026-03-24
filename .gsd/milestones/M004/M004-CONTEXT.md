# M004: Dress-Up to Coloring Pipeline

**Gathered:** 2026-03-23
**Status:** Ready for planning

## Project Description

Connect the dress-up and coloring activities so the mermaid a kid customizes flows directly into coloring. Add a "Color This!" button to dress-up that navigates to the coloring canvas with a matching B&W outline of the active character. Pre-generate 9 coloring outlines (one per dress-up character) via the AI pipeline and bundle as static assets. Also refresh all navigation and activity icons to be semantically meaningful, and fix the 5 blank coloring gallery pages.

## Why This Milestone

The two activities are currently separate worlds — dress-up and coloring share no state. A kid who builds "her" mermaid can't color that same mermaid. This is the feature she'd expect: "I made this mermaid, now I want to color her." The icon fix and art fix are polish that should ship together.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Pick a mermaid in dress-up, tap "Color This!", and immediately land on a coloring canvas with that mermaid's B&W outline
- See all 9 coloring gallery pages with real mermaid art (no blank tiles)
- See semantically meaningful icons throughout the app (mermaid tail for dress-up, palette for coloring, house for home)

### Entry point / environment

- Entry point: https://mermaids.chriskaschner.com
- Environment: iPad Safari via GitHub Pages
- Live dependencies involved: OpenAI API (for art generation during pipeline run, not at runtime)

## Completion Class

- Contract complete means: E2E tests prove "Color This!" navigation works, 9 dressup-character outlines exist as SVG assets, icon SVGs are semantically correct, all 9 coloring pages have real art, 104+ tests pass
- Integration complete means: The full dress-up → coloring flow works in a browser with real SVG assets loading
- Operational complete means: Deployed to GitHub Pages and verified on the live site

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- Kid flow: select mermaid-3 in dress-up → tap "Color This!" → coloring canvas loads mermaid-3's outline → can paint/fill on it
- Coloring gallery: all 9 thumbnails show real art, all are tappable and load correctly
- Icons: nav bar and home screen icons are visually distinct and semantically match their activity

## Risks and Unknowns

- AI-generated coloring outlines for dress-up characters may not produce clean flood-fillable shapes — the existing coloring pages were purpose-prompted for outlines, the dress-up characters were prompted for full-color kawaii art
- The 9 outlines must look recognizably like "the same mermaid" the kid just customized — full-color kawaii vs simplified B&W outline may feel disconnected
- Pages 5-9 coloring SVG generation requires an OpenAI API key and may produce low-quality output

## Existing Codebase / Prior Art

- `frontend/js/dressup.js` — Gallery swap logic, state.activeCharacter tracks current character ID, CHARACTERS array has mermaid-1 through mermaid-9
- `frontend/js/coloring.js` — COLORING_PAGES array with {id, label, file} entries, initColoringCanvas(svgUrl, container) rasterizes SVG onto canvas
- `frontend/js/app.js` — Hash router (#/home, #/dressup, #/coloring), renderDressUp() and openColoringPage(pageId) functions, inline SVG icons for nav and home
- `frontend/index.html` — Nav bar with 3 icon links (home, dressup, coloring)
- `src/mermaids/pipeline/prompts.py` — COLORING_BASE_PROMPT and COLORING_PAGES for coloring art generation
- `scripts/generate_coloring.py` — Generates coloring page PNGs from prompts
- `scripts/trace_all.py` — Converts PNGs to SVGs via vtracer
- `frontend/assets/svg/dressup/mermaid-{1-9}.svg` — 9 full-color kawaii character SVGs (30KB each)
- `frontend/assets/svg/coloring/page-{1-4}*.svg` — 4 real coloring SVGs (51-75KB), pages 5-9 are 170-byte empty shells

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions.

## Relevant Requirements

- PIPE-01 — Dress-up → coloring pipeline (primary)
- PIPE-02 — "Color This!" button in dress-up
- PIPE-03 — 9 pre-generated coloring outlines
- ICON-01 — Semantically meaningful icons
- COLR-04 — All 9 coloring gallery pages show real art

## Scope

### In Scope

- "Color This!" button in dress-up view that navigates to coloring with matching character outline
- 9 pre-generated coloring outline SVGs for dress-up characters (via AI pipeline)
- New route or parameter to load a specific character's outline on the coloring canvas (bypassing gallery)
- Full icon refresh: nav bar (3 icons) + home screen activity buttons (2 icons)
- Generate and deploy real SVG art for coloring pages 5-9
- All existing tests continue passing + new tests for the pipeline flow

### Out of Scope / Non-Goals

- Part-mixing (combining hair from mermaid-3 with tail from mermaid-7) — future feature
- Live AI generation at runtime — all outlines are pre-generated static assets
- Scene backgrounds — deferred to future milestone (SCENE-01)
- Animation — deferred to future milestone (ANIM-01)

## Technical Constraints

- No build step — vanilla JS, ES modules, static file serving
- Must work in iPad Safari with 60pt+ touch targets
- AI art generation happens offline via pipeline scripts, not at runtime
- OpenAI API key required for generating new art assets (pipeline only)
- CSS gallery layout uses max-height: 260px constraint for Playwright viewport compatibility

## Integration Points

- OpenAI gpt-image-1 API — Used during pipeline art generation (offline, not runtime)
- vtracer — Raster-to-SVG conversion for generated PNGs
- GitHub Pages — Static deployment target
- GitHub Actions — CI test gate before deploy

## Open Questions

- What prompt should be used for dress-up character coloring outlines? The existing COLORING_BASE_PROMPT targets generic scenes; the dress-up outlines need to match specific character designs (mermaid-1 through mermaid-9 with their distinct hair/eyes/tail). May need per-character prompts derived from the original dress-up generation prompts.
