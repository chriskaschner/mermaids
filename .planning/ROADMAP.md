# Roadmap: Mermaid Create & Play

## Overview

This roadmap delivers a mermaid-themed creative activity app for a 6-year-old on iPad Safari. Phase 1 establishes the SVG foundation, art asset pipeline, touch interaction, and navigation shell -- the hard dependencies everything else sits on. Phase 2 delivers the dress-up activity (the primary creative mechanic and minimum viable delight). Phase 3 delivers coloring pages (the second activity, completing the app). Scene builder, print, gallery, and audio are deferred to v2.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - SVG rendering, art assets, touch interaction, navigation shell on iPad Safari (completed 2026-03-09)
- [ ] **Phase 2: Dress-Up** - Mermaid customization with swappable parts, colors, accessories, and undo
- [ ] **Phase 3: Coloring** - Tap-to-fill coloring pages with color palette and undo

## Phase Details

### Phase 1: Foundation
**Goal**: A child can open the app on an iPad, see a watercolor-styled mermaid rendered as SVG, interact with it via touch, and navigate between activity screens
**Depends on**: Nothing (first phase)
**Requirements**: FOUN-01, FOUN-02, FOUN-03, FOUN-04, NAVG-01, NAVG-02
**Success Criteria** (what must be TRUE):
  1. App loads in iPad Safari and displays an inline SVG mermaid with watercolor-style art
  2. Tapping SVG elements on a real iPad triggers visible feedback (color change, highlight, or animation)
  3. All interactive elements have tap targets of 60pt or larger
  4. Home screen shows two large icon buttons (dress-up and coloring) and tapping either navigates to that activity screen
  5. Navigation icons are visible from every activity screen and switching between them works with a single tap
**Plans:** 3/3 plans complete

Plans:
- [x] 01-01-PLAN.md -- Project scaffolding, FastAPI server, iPad HTML/CSS shell, test infrastructure
- [x] 01-02-PLAN.md -- Art pipeline (vtracer) and proof-of-concept mermaid SVG with tappable regions
- [x] 01-03-PLAN.md -- Hash router, touch interaction, sparkle feedback, navigation, and visual verification

### Phase 2: Dress-Up
**Goal**: A child can build her own mermaid by mixing and matching tails, hair, accessories, and colors -- and see a sparkle animation when she's done
**Depends on**: Phase 1
**Requirements**: DRSS-01, DRSS-02, DRSS-03, DRSS-04, DRSS-05, DRSS-06, DRSS-07
**Success Criteria** (what must be TRUE):
  1. A base mermaid character is visible on the dress-up screen
  2. Tapping tail options swaps the mermaid's tail (3-4 options), tapping hair options swaps hair (3-4 options), and tapping accessory options adds/swaps crowns and accessories (3-4 options)
  3. Tapping a color swatch recolors the currently selected mermaid part (8-12 color options available)
  4. Tapping an undo button reverts the last change
  5. A sparkle/bubble animation plays when the mermaid has all parts selected
**Plans:** 2 plans

Plans:
- [ ] 02-01-PLAN.md -- Test scaffold, restructured mermaid SVG with variant system, dressup.js state module
- [ ] 02-02-PLAN.md -- Selection panel UI, color palette, undo, celebration animation, visual verification

### Phase 3: Coloring
**Goal**: A child can pick a mermaid coloring page, tap regions to fill them with color, and undo mistakes
**Depends on**: Phase 2
**Requirements**: COLR-01, COLR-02, COLR-03, COLR-04
**Success Criteria** (what must be TRUE):
  1. The coloring screen presents 4-6 mermaid-themed coloring page thumbnails to choose from
  2. Tapping a region on a coloring page fills it with the currently selected color
  3. The same 8-12 color swatch palette from dress-up is available for coloring
  4. Tapping an undo button reverts the last color fill
**Plans**: TBD

Plans:
- [ ] 03-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete   | 2026-03-09 |
| 2. Dress-Up | 0/2 | In progress | - |
| 3. Coloring | 0/0 | Not started | - |
