# Requirements: Mermaid Create & Play

**Defined:** 2026-03-09
**Core Value:** A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages -- with zero friction and pure delight.

## v1.1 Requirements

Requirements for v1.1 Art & Deploy milestone. Each maps to roadmap phases.

### Art Pipeline

- [x] **ARTP-01**: Local script generates kawaii mermaid coloring page PNGs via OpenAI gpt-image-1 API
- [x] **ARTP-02**: Local script traces generated PNGs to SVG via vtracer
- [ ] **ARTP-03**: Local script generates dress-up mermaid variant parts (tails, hair, accessories) with consistent alignment via edit API masks
- [ ] **ARTP-04**: Generated SVG assets are committed to frontend/assets/svg/ for static serving

### Coloring

- [ ] **CLRV-01**: Coloring pages use canvas-based flood fill at tap point (replaces region-based fill)
- [ ] **CLRV-02**: SVG line art overlays canvas for crisp retina-quality outlines
- [ ] **CLRV-03**: Flood fill handles anti-aliased edges with configurable tolerance
- [ ] **CLRV-04**: Canvas memory is released when navigating away from coloring (iPad Safari safety)
- [ ] **CLRV-05**: Undo reverts last flood-fill operation via ImageData snapshots

### Dress-Up

- [ ] **DRSV-01**: Dress-up mermaid uses AI-generated kawaii art (replaces hand-crafted SVG)
- [ ] **DRSV-02**: SVG defs+use variant swap works with new AI-generated part assets
- [ ] **DRSV-03**: Color recoloring works on kawaii flat-color style parts

### Deployment

- [ ] **DPLY-01**: frontend/ directory deploys to GitHub Pages as static site
- [ ] **DPLY-02**: All asset paths are relative (no absolute /assets/ paths)
- [ ] **DPLY-03**: App is accessible on iPad Safari via GitHub Pages URL

## Future Requirements

Deferred to later milestones. Tracked but not in current roadmap.

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
| GitHub Actions CI | Local scripts sufficient for art generation, manual deploy |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARTP-01 | Phase 4 | Complete (04-01) |
| ARTP-02 | Phase 4 | Complete (04-01) |
| ARTP-03 | Phase 4 | Pending |
| ARTP-04 | Phase 4 | Pending |
| CLRV-01 | Phase 5 | Pending |
| CLRV-02 | Phase 5 | Pending |
| CLRV-03 | Phase 5 | Pending |
| CLRV-04 | Phase 5 | Pending |
| CLRV-05 | Phase 5 | Pending |
| DRSV-01 | Phase 6 | Pending |
| DRSV-02 | Phase 6 | Pending |
| DRSV-03 | Phase 6 | Pending |
| DPLY-01 | Phase 7 | Pending |
| DPLY-02 | Phase 7 | Pending |
| DPLY-03 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-10 after 04-01 completion*
