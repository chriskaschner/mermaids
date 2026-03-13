# Requirements: Mermaid Create & Play

**Defined:** 2026-03-12
**Core Value:** A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages -- with zero friction and pure delight.

## v1.2 Requirements

Requirements for Mermaid Art Rework milestone. Each maps to roadmap phases.

### Dress-Up Art

- [ ] **DRSU-01**: User sees a single base mermaid (not different mermaids per item)
- [ ] **DRSU-02**: User can swap between multiple hair style variants
- [ ] **DRSU-03**: User can swap between multiple eye style variants
- [ ] **DRSU-04**: User can swap between multiple tail style variants

### Coloring Art

- [ ] **COLR-01**: Coloring pages feature hair/eyes/tail variety across pages
- [ ] **COLR-02**: Hair regions are closed shapes that flood-fill can color
- [ ] **COLR-03**: Tail regions are closed shapes that flood-fill can color

### Tech Debt

- [ ] **DEBT-01**: Debug overlay removed from app.js
- [ ] **DEBT-02**: WebKit sparkle E2E test failures fixed
- [ ] **DEBT-03**: AI-generated hair/tail region overlap fixed

## Future Requirements

Deferred to future milestone. Tracked but not in current roadmap.

### Integration

- **INTG-01**: Dress-up-to-coloring: the mermaid you customize in dress-up becomes the coloring page you color

### Content

- **CONT-01**: Scene builder: place customized mermaid into underwater scene backgrounds
- **CONT-02**: Print coloring pages: export/print uncolored outlines for real-world coloring
- **CONT-03**: Save creations: gallery of completed mermaids and colored pages
- **CONT-04**: Themed coloring page sets (Coral Reef, Mermaid Castle collections)

### Polish

- **PLSH-01**: Sound effects on interaction (tap, place, sparkle) with mute button

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| New activities (games, drawing) | Not the focus -- fixing existing art quality |
| Color picker changes | Preset swatches work fine, art is the problem |
| New UI/navigation changes | UI works, art assets are what need fixing |
| Dress-up-to-coloring bridge | Future milestone -- get the art right first |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DRSU-01 | Phase 8 | Pending |
| DRSU-02 | Phase 8 | Pending |
| DRSU-03 | Phase 8 | Pending |
| DRSU-04 | Phase 8 | Pending |
| DEBT-03 | Phase 8 | Pending |
| COLR-01 | Phase 9 | Pending |
| COLR-02 | Phase 9 | Pending |
| COLR-03 | Phase 9 | Pending |
| DEBT-01 | Phase 10 | Pending |
| DEBT-02 | Phase 10 | Pending |

**Coverage:**
- v1.2 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-03-12*
*Last updated: 2026-03-12 after roadmap creation*
