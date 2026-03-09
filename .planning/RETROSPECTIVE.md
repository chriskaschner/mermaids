# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 -- MVP

**Shipped:** 2026-03-09
**Phases:** 3 | **Plans:** 7 | **Sessions:** 1

### What Was Built
- FastAPI + vanilla JS web app with iPad-optimized touch interaction
- Mermaid dress-up with SVG variant system (10 part variants, color swatches, undo, celebration sparkle)
- 4 mermaid coloring pages with tap-to-fill, gallery view, undo
- vtracer art pipeline for raster-to-SVG conversion
- 37 Playwright E2E tests across 5 suites

### What Worked
- Coarse granularity (3 phases, 7 plans) matched weekend scope perfectly
- SVG defs+use pattern made variant swapping trivial (single setAttribute call)
- TDD approach with Playwright caught real issues (pointer interception, SVG hit areas)
- Consistent 3min/plan velocity across all phases
- No framework, no build step -- shipped entire app in one session

### What Was Inefficient
- PoC mermaid SVG was hand-crafted despite having vtracer pipeline (pipeline unused for final assets)
- COLORS array duplicated between dressup.js and coloring.js (separate state lifecycles justified it, but could share constants)
- Fetch path inconsistency (absolute vs relative) crept in across phases

### Patterns Established
- SVG `<defs>+<use>` for swappable visual variants
- `data-region` attribute convention for interactive SVG areas
- Pointer event delegation on SVG root with `closest('[data-region]')` traversal
- Undo closures capturing per-element state snapshots
- Bottom nav bar for child thumb reach, hidden on home screen

### Key Lessons
1. Hand-crafted SVGs with intentional region structure beat pipeline-traced SVGs for interactive content -- structure matters more than tracing fidelity
2. One pointerdown listener with event delegation handles all touch interaction cleanly -- no per-element listener management
3. Playwright iPad emulation catches real touch/pointer issues that unit tests miss

### Cost Observations
- Model mix: balanced profile throughout
- Sessions: 1 (entire v1.0 in single session)
- Notable: 7 plans in ~21 minutes total execution time

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 1 | 3 | Initial project -- coarse granularity, TDD approach |

### Cumulative Quality

| Milestone | Tests | Coverage | Tech Debt Items |
|-----------|-------|----------|-----------------|
| v1.0 | 37 | E2E-focused | 2 minor |

### Top Lessons (Verified Across Milestones)

1. (First milestone -- lessons to be verified in v1.1+)
