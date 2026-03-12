# Milestones

## v1.1 Art & Deploy (Shipped: 2026-03-12)

**Delivered:** AI-generated kawaii mermaid art, canvas flood-fill coloring, and GitHub Pages deployment -- the app is live at mermaids.chriskaschner.com and usable on her iPad.

**Phases completed:** 4-7 (10 plans total)

**Key accomplishments:**
- AI art generation pipeline: OpenAI gpt-image-1 + vtracer tracing + SVG assembly for kawaii mermaid assets
- Canvas-based flood fill with SVG overlay for crisp retina-quality coloring outlines
- Dress-up mermaid upgraded to AI-generated kawaii art with async preview thumbnails and color sync
- GitHub Pages deployment with CI test gate, custom domain, and HTTPS enforcement
- iPad Safari touch fix: z-index stacking and stopPropagation guards for reliable interaction

**Stats:**
- 46 source files changed, 15,098 insertions, 1,003 deletions
- 5,382 LOC (Python + JS + CSS + HTML)
- 4 phases, 10 plans
- 3 days (2026-03-09 to 2026-03-12)
- 92 commits

**Git range:** d36ce6f..839cf7b

**Tech debt carried forward:**
- ARTP-04 visual quality needs human validation after API run
- Debug overlay in app.js should be removed
- 2/62 sparkle E2E tests fail on WebKit (pre-existing)
- AI-generated hair regions overlap tail regions (pre-existing)

**What's next:** TBD -- next milestone via `/gsd:new-milestone`

---

## v1.0 MVP (Shipped: 2026-03-09)

**Phases completed:** 3 phases, 7 plans
**Lines of code:** 2,172 (Python + JS + HTML + CSS)
**Tests:** 37 passing (5 suites)
**Timeline:** 2026-03-09 (single day)
**Git range:** 7f8bcfa..ff5fb1f

**Key accomplishments:**
- FastAPI static SPA with iPad-optimized shell and 60pt tap targets
- Art pipeline (vtracer) for raster-to-SVG conversion with watercolor filter
- Hash router, touch interaction with sparkle feedback, bottom navigation
- Mermaid dress-up with 10 SVG part variants, color swatches, undo
- Selection panel UI with celebration sparkle animation
- 4 mermaid coloring pages with tap-to-fill, gallery, color palette, undo

**Delivered:** A 6-year-old can open the app on an iPad, build her own mermaid with mix-and-match parts and colors, and color mermaid pages -- all with touch-friendly controls and sparkle feedback.

**Tech debt carried forward:**
- Fetch path inconsistency (absolute vs relative SVG paths)
- No E2E test for cross-view state isolation round-trip

---

