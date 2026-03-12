# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.1 -- Art & Deploy

**Shipped:** 2026-03-12
**Phases:** 4 | **Plans:** 10 | **Sessions:** ~5

### What Was Built
- AI art generation pipeline: OpenAI gpt-image-1 + vtracer tracing + SVG assembly (Phase 4)
- Canvas-based flood fill with scanline algorithm, anti-aliased edge tolerance, SVG overlay for crisp lines (Phase 5)
- Dress-up mermaid upgraded to AI-generated kawaii art with async preview thumbnails and per-variant color memory (Phase 6)
- GitHub Pages deployment with CI test gate, custom domain, HTTPS enforcement (Phase 7)
- iPad Safari touch interaction fixes (z-index stacking, stopPropagation guards)

### What Worked
- Canvas+SVG hybrid approach solved the "crisp lines + pixel fill" problem elegantly
- Edit API with spatial masks kept AI-generated variants aligned within viewBox
- Iterative gap closure (07-03, 07-04) was effective for iPad Safari issues -- isolate, fix, verify on real device
- Pipeline module pattern (config/prompts/generate/edit/assemble) kept art generation organized
- releaseCanvas() pattern prevented iPad Safari memory issues

### What Was Inefficient
- iPad Safari touch bugs required 2 extra gap-closure plans (07-03, 07-04) -- could have caught earlier with real-device testing before declaring phase complete
- FILL_TOLERANCE changed from 32 to 48 during development -- initial value based on theory, real SVGs needed higher tolerance
- 7 commits accumulated locally without pushing to remote -- CI pipeline fell behind, deployment gap at milestone end
- Sparkle test selector became stale after SVG structure changed (data-region="tail" no longer exists) -- tests should update when assets change

### Patterns Established
- Canvas+SVG hybrid: canvas for pixel operations, SVG overlay with pointer-events:none for vector crispness
- Flood fill scanline algorithm with tolerance-based color matching for anti-aliased edges
- Preview SVG cache with color overlay (cache original text, apply colors after DOM insertion)
- z-index hierarchy for iOS Safari: nav=5, view=10, panel=20
- stopPropagation on all interactive click handlers to prevent tap-through on mobile
- BASE_URL env var pattern for CI testing against static file server

### Key Lessons
1. Real-device testing on iPad Safari is non-negotiable before declaring deployment requirements satisfied -- Playwright WebKit emulation does not catch iOS-specific layering and touch issues
2. Push commits to remote after each phase completion, not at milestone end -- keeps CI/CD current and catches integration issues early
3. AI-generated SVG assets need explicit tolerance tuning -- vtracer anti-aliasing creates different edge profiles than hand-drawn art
4. Gap closure plans are a healthy pattern, not a failure -- they surface real issues that automated tests miss

### Cost Observations
- Model mix: balanced profile (sonnet for agents, opus for orchestration)
- Sessions: ~5 across 3 days
- Notable: Phase 4-6 plans averaged 4-5 min each; Phase 7 took longer due to real-device verification loops

---

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
| v1.1 | ~5 | 4 | AI art pipeline, gap closure pattern, real-device verification |

### Cumulative Quality

| Milestone | Tests | Coverage | Tech Debt Items |
|-----------|-------|----------|-----------------|
| v1.0 | 37 | E2E-focused | 2 minor |
| v1.1 | 62 | E2E + unit (flood fill, pipeline) | 5 (2 pre-existing) |

### Top Lessons (Verified Across Milestones)

1. Playwright catches real touch/pointer issues -- verified in both v1.0 (hit area bugs) and v1.1 (iPad Safari layering)
2. SVG defs+use remains the right pattern for swappable parts -- scaled from hand-crafted (v1.0) to AI-generated (v1.1) seamlessly
3. Push to remote frequently -- v1.0 was single-session so no gap; v1.1 accumulated 7 unpushed commits causing deployment lag
