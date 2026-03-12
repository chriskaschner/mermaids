# Roadmap: Mermaid Create & Play

## Milestones

- [x] **v1.0 MVP** -- Phases 1-3 (shipped 2026-03-09)
- [x] **v1.1 Art & Deploy** -- Phases 4-7 (shipped 2026-03-12)

## Phases

<details>
<summary>v1.0 MVP (Phases 1-3) -- SHIPPED 2026-03-09</summary>

- [x] Phase 1: Foundation (3/3 plans) -- completed 2026-03-09
- [x] Phase 2: Dress-Up (2/2 plans) -- completed 2026-03-09
- [x] Phase 3: Coloring (2/2 plans) -- completed 2026-03-09

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### v1.1 Art & Deploy

- [x] **Phase 4: Art Pipeline** - Generate kawaii mermaid SVG assets via OpenAI gpt-image-1 and vtracer
- [x] **Phase 5: Flood-Fill Coloring** - Replace region-based coloring with canvas flood fill and SVG overlay
- [x] **Phase 6: Dress-Up Art Swap** - Replace hand-crafted mermaid with AI-generated kawaii art and variants
- [x] **Phase 7: GitHub Pages Deployment** - Deploy static site with relative paths, accessible on iPad (completed 2026-03-12)

## Phase Details

### Phase 4: Art Pipeline
**Goal**: Developer can generate consistent kawaii mermaid SVG assets (coloring pages and dress-up parts) from a single script workflow
**Depends on**: Nothing (first phase of v1.1)
**Requirements**: ARTP-01, ARTP-02, ARTP-03, ARTP-04
**Success Criteria** (what must be TRUE):
  1. Running the generation script produces kawaii mermaid coloring page PNGs via gpt-image-1 API
  2. Running the tracing script converts generated PNGs to clean SVG line art via vtracer
  3. Running the variant generation script produces dress-up part variants (tails, hair, accessories) with consistent spatial alignment using edit API masks
  4. All generated SVG assets exist in frontend/assets/svg/ and render correctly in a browser
**Plans:** 2 plans

Plans:
- [x] 04-01-PLAN.md -- Shared pipeline infra + coloring page generation and tracing (ARTP-01, ARTP-02)
- [x] 04-02-PLAN.md -- Dress-up variant generation via edit API + SVG assembly to frontend (ARTP-03, ARTP-04)

### Phase 5: Flood-Fill Coloring
**Goal**: Child can color any AI-generated mermaid page by tapping to flood-fill regions, with crisp outlines and undo support
**Depends on**: Phase 4 (needs coloring page SVGs to render and test against)
**Requirements**: CLRV-01, CLRV-02, CLRV-03, CLRV-04, CLRV-05
**Success Criteria** (what must be TRUE):
  1. Tapping a white region on a coloring page fills that region with the selected color (canvas flood fill)
  2. Line art remains crisp and unaffected by fill operations (SVG overlay at retina resolution)
  3. Fill correctly stops at anti-aliased edges without bleeding through lines
  4. Tapping undo reverts the last fill operation, restoring the previous state
  5. Navigating away from coloring and back does not crash or degrade performance on iPad Safari
**Plans:** 2 plans

Plans:
- [x] 05-01-PLAN.md -- Flood fill algorithm + canvas coloring module (CLRV-01, CLRV-03, CLRV-05)
- [x] 05-02-PLAN.md -- App integration with canvas+SVG hybrid + E2E tests (CLRV-01, CLRV-02, CLRV-03, CLRV-04, CLRV-05)

### Phase 6: Dress-Up Art Swap
**Goal**: Child can mix and match kawaii mermaid parts with the same dress-up interaction, now using AI-generated art
**Depends on**: Phase 4 (needs dress-up mermaid SVG assets)
**Requirements**: DRSV-01, DRSV-02, DRSV-03
**Success Criteria** (what must be TRUE):
  1. Dress-up screen displays AI-generated kawaii mermaid (replaces hand-crafted SVG)
  2. Tapping a part variant in the selection panel swaps the mermaid part on screen (defs+use mechanism works with new assets)
  3. Tapping a color swatch recolors the selected part across the kawaii flat-color art style
**Plans:** 2 plans

Plans:
- [x] 06-01-PLAN.md -- Asset pipeline: deploy variant SVGs to frontend, strip background rects, regenerate mermaid.svg (DRSV-01, DRSV-02)
- [x] 06-02-PLAN.md -- Frontend art swap: async preview thumbnails, color sync, relative paths, E2E tests (DRSV-01, DRSV-02, DRSV-03)

### Phase 7: GitHub Pages Deployment
**Goal**: The app is live on GitHub Pages and usable on her iPad without running a local server
**Depends on**: Phase 5, Phase 6 (all features must work before deploying)
**Requirements**: DPLY-01, DPLY-02, DPLY-03
**Success Criteria** (what must be TRUE):
  1. The frontend/ directory is deployed to GitHub Pages as a static site
  2. All asset references use relative paths (no broken loads from absolute /assets/ paths)
  3. Opening the GitHub Pages URL on iPad Safari loads the app and both activities work correctly
**Plans:** 4/4 plans complete

Plans:
- [x] 07-01-PLAN.md -- CI test job (static server E2E) + conftest BASE_URL support + deploy gate (DPLY-01, DPLY-02, DPLY-03)
- [x] 07-02-PLAN.md -- Custom domain DNS + GitHub Pages Settings + real iPad verification (DPLY-01 satisfied; DPLY-03 NOT satisfied)
- [x] 07-03-PLAN.md -- Gap closure: fix z-index layering + event propagation guards + debug overlay for iPad Safari diagnosis (DPLY-03)
- [x] 07-04-PLAN.md -- Gap closure: real iPad Safari verification + HTTPS enforcement (DPLY-01, DPLY-02, DPLY-03)

## Progress

**Execution Order:** Phase 4 -> 5 -> 6 -> 7

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-09 |
| 2. Dress-Up | v1.0 | 2/2 | Complete | 2026-03-09 |
| 3. Coloring | v1.0 | 2/2 | Complete | 2026-03-09 |
| 4. Art Pipeline | v1.1 | 2/2 | Complete | 2026-03-10 |
| 5. Flood-Fill Coloring | v1.1 | 2/2 | Complete | 2026-03-10 |
| 6. Dress-Up Art Swap | v1.1 | 2/2 | Complete | 2026-03-10 |
| 7. GitHub Pages Deployment | v1.1 | 4/4 | Complete | 2026-03-12 |
