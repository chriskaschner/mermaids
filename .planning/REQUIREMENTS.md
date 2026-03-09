# Requirements: Mermaid Create & Play

**Defined:** 2026-03-09
**Core Value:** A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages -- with zero friction and pure delight.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Dress-Up

- [ ] **DRSS-01**: User can view a base mermaid character on screen
- [ ] **DRSS-02**: User can swap between 3-4 tail options by tapping
- [ ] **DRSS-03**: User can swap between 3-4 hair style options by tapping
- [ ] **DRSS-04**: User can add/swap crowns and accessories (3-4 options)
- [ ] **DRSS-05**: User can recolor mermaid parts by tapping color swatches (8-12 colors)
- [ ] **DRSS-06**: User can undo last action with a single tap
- [ ] **DRSS-07**: Sparkle/bubble animation plays when all parts are selected

### Coloring

- [ ] **COLR-01**: User can view 4-6 mermaid-themed coloring pages
- [ ] **COLR-02**: User can tap a region on a coloring page to fill it with the selected color
- [ ] **COLR-03**: User can select colors from the same 8-12 swatch palette
- [ ] **COLR-04**: User can undo last color fill with a single tap

### Navigation

- [ ] **NAVG-01**: Home screen shows dress-up and coloring as large icon buttons (no text required)
- [ ] **NAVG-02**: User can switch between activities from any screen via icon navigation

### Foundation

- [ ] **FOUN-01**: All tap targets are 60pt+ for a 6-year-old's motor control
- [ ] **FOUN-02**: App works in iPad Safari with touch interaction
- [x] **FOUN-03**: Consistent watercolor art style across all assets
- [ ] **FOUN-04**: All interactions provide instant visual feedback (no loading states)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Scene Builder

- **SCEN-01**: User can place customized mermaid into underwater scene backgrounds
- **SCEN-02**: User can add decorative elements (fish, coral, treasure) to scenes
- **SCEN-03**: 3-5 underwater scene backgrounds available

### Print

- **PRNT-01**: User can print coloring page outlines for real-world coloring
- **PRNT-02**: Printed pages are clean outlines suitable for crayons

### Gallery

- **GALR-01**: User can save completed mermaids and colored pages
- **GALR-02**: User can view gallery of saved creations
- **GALR-03**: Auto-save on meaningful changes

### Audio

- **AUDI-01**: Sound effects on interaction (tap, place, sparkle)
- **AUDI-02**: Mute button for parents

### Polish

- **POLH-01**: Themed coloring page sets (Coral Reef, Mermaid Castle collections)
- **POLH-02**: Stamp tool for decorating scenes

## Out of Scope

| Feature | Reason |
|---------|--------|
| Free drawing / canvas painting | High complexity, imprecise for a 6-year-old on touch |
| Mini-games (matching, puzzles) | Not what she gravitates to in Crayola app |
| User accounts / login | She's 6, COPPA compliance is a legal minefield |
| Cloud sync | Weekend-project-breaking complexity |
| Sharing / social | COPPA, moderation, abuse risk |
| Native iPad app | Web app keeps it simple, no App Store needed |
| Text input / labels | A 6-year-old reads at beginner level |
| Complex color picker | HSL/hex too complex, use preset swatches |
| Zoom / pan | Spatial navigation is confusing for a child |
| Onboarding tutorial | If the app needs a tutorial, it's too complex |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUN-01 | Phase 1 | Partial (01-01: CSS foundation) |
| FOUN-02 | Phase 1 | Partial (01-01: viewport + web-app meta) |
| FOUN-03 | Phase 1 | Complete (01-02: watercolor SVG filter + mermaid SVG) |
| FOUN-04 | Phase 1 | Pending |
| NAVG-01 | Phase 1 | Pending |
| NAVG-02 | Phase 1 | Pending |
| DRSS-01 | Phase 2 | Pending |
| DRSS-02 | Phase 2 | Pending |
| DRSS-03 | Phase 2 | Pending |
| DRSS-04 | Phase 2 | Pending |
| DRSS-05 | Phase 2 | Pending |
| DRSS-06 | Phase 2 | Pending |
| DRSS-07 | Phase 2 | Pending |
| COLR-01 | Phase 3 | Pending |
| COLR-02 | Phase 3 | Pending |
| COLR-03 | Phase 3 | Pending |
| COLR-04 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after roadmap creation*
