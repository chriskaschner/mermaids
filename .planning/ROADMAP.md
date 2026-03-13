# Roadmap: Mermaid Create & Play

## Milestones

- [x] **v1.0 MVP** -- Phases 1-3 (shipped 2026-03-09)
- [x] **v1.1 Art & Deploy** -- Phases 4-7 (shipped 2026-03-12)
- [ ] **v1.2 Mermaid Art Rework** -- Phases 8-10 (in progress)

## Phases

<details>
<summary>v1.0 MVP (Phases 1-3) -- SHIPPED 2026-03-09</summary>

- [x] Phase 1: Foundation (3/3 plans) -- completed 2026-03-09
- [x] Phase 2: Dress-Up (2/2 plans) -- completed 2026-03-09
- [x] Phase 3: Coloring (2/2 plans) -- completed 2026-03-09

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>v1.1 Art & Deploy (Phases 4-7) -- SHIPPED 2026-03-12</summary>

- [x] Phase 4: Art Pipeline (2/2 plans) -- completed 2026-03-10
- [x] Phase 5: Flood-Fill Coloring (2/2 plans) -- completed 2026-03-10
- [x] Phase 6: Dress-Up Art Swap (2/2 plans) -- completed 2026-03-10
- [x] Phase 7: GitHub Pages Deployment (4/4 plans) -- completed 2026-03-12

Full details: `.planning/milestones/v1.1-ROADMAP.md`

</details>

### v1.2 Mermaid Art Rework (In Progress)

**Milestone Goal:** Fix dress-up and coloring art so both use a single base mermaid with swappable parts (hair, eyes, tail) and closed hair/tail regions for paint bucket.

- [ ] **Phase 8: Dress-Up Art Rework** - Generate single-base mermaid with swappable hair, eyes, and tail parts; wire into dress-up UI
- [ ] **Phase 9: Coloring Art Rework** - Generate coloring pages with hair/eyes/tail variety and closed fillable regions
- [ ] **Phase 10: Cleanup & Stability** - Remove debug overlay and fix WebKit sparkle test failures

## Phase Details

### Phase 8: Dress-Up Art Rework
**Goal**: User sees a single unified mermaid whose hair, eyes, and tail can be swapped independently
**Depends on**: Phase 7 (existing dress-up infrastructure)
**Requirements**: DRSU-01, DRSU-02, DRSU-03, DRSU-04, DEBT-03
**Success Criteria** (what must be TRUE):
  1. User sees one consistent mermaid body -- not visually different mermaids per hair/eye/tail choice
  2. User can tap hair swatches and the mermaid's hair changes while everything else stays the same
  3. User can tap eye swatches and the mermaid's eyes change while everything else stays the same
  4. User can tap tail swatches and the mermaid's tail changes while everything else stays the same
  5. Hair and tail art regions do not visually overlap or bleed into each other
**Plans:** 2/3 plans executed
Plans:
- [ ] 08-01-PLAN.md -- Pipeline rework: prompts, regions, masks, multi-layer SVG assembly
- [ ] 08-02-PLAN.md -- Frontend rework: multi-part swap, eyes tab, per-part recoloring
- [ ] 08-03-PLAN.md -- Art generation: run pipeline, deploy assets, visual verification

### Phase 9: Coloring Art Rework
**Goal**: Coloring pages show mermaids with varied hair, eyes, and tail -- and flood-fill works on all regions including hair and tail
**Depends on**: Phase 8 (consistent base mermaid art established)
**Requirements**: COLR-01, COLR-02, COLR-03
**Success Criteria** (what must be TRUE):
  1. Different coloring pages show different hair, eye, and tail styles (not just accessory variation)
  2. User can tap inside a hair region and flood-fill colors the entire hair area without leaking out
  3. User can tap inside a tail region and flood-fill colors the entire tail area without leaking out
**Plans**: TBD

### Phase 10: Cleanup & Stability
**Goal**: Debug artifacts removed and E2E test suite passes cleanly on all browsers
**Depends on**: Phase 9
**Requirements**: DEBT-01, DEBT-02
**Success Criteria** (what must be TRUE):
  1. No debug overlay or console-exposed debug UI appears in the app during normal use
  2. All sparkle E2E tests pass on WebKit (the 2 pre-existing failures are resolved)
  3. CI test gate passes green on all browsers before any deploy
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-09 |
| 2. Dress-Up | v1.0 | 2/2 | Complete | 2026-03-09 |
| 3. Coloring | v1.0 | 2/2 | Complete | 2026-03-09 |
| 4. Art Pipeline | v1.1 | 2/2 | Complete | 2026-03-10 |
| 5. Flood-Fill Coloring | v1.1 | 2/2 | Complete | 2026-03-10 |
| 6. Dress-Up Art Swap | v1.1 | 2/2 | Complete | 2026-03-10 |
| 7. GitHub Pages Deployment | v1.1 | 4/4 | Complete | 2026-03-12 |
| 8. Dress-Up Art Rework | 2/3 | In Progress|  | - |
| 9. Coloring Art Rework | v1.2 | 0/? | Not started | - |
| 10. Cleanup & Stability | v1.2 | 0/? | Not started | - |
