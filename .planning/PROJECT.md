# Mermaid Create & Play

## What This Is

A web-based creative activity app for a 6-year-old, themed entirely around mermaids. Two activities: dress-up (mix and match tails, hair, accessories, and colors on a mermaid character) and coloring (tap-to-fill mermaid-themed pages). Built with a dreamy watercolor aesthetic, designed for iPad Safari with 60pt+ touch targets and zero-instruction usability.

## Core Value

A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages -- with zero friction and pure delight.

## Requirements

### Validated

- [x] Mermaid dress-up: mix and match tail colors, hair styles, crowns, and accessories -- v1.0
- [x] Coloring pages: mermaid-themed outlines to color digitally -- v1.0
- [x] Watercolor art style: dreamy, soft, painterly visual aesthetic throughout -- v1.0
- [x] Touch-friendly: designed for iPad touch interaction, big tap targets, no tiny UI -- v1.0

### Active

- [ ] AI art generation pipeline (OpenAI API + kawaii mermaid prompts + vtracer tracing)
- [ ] Upgraded coloring pages with AI-generated art and flood-fill interaction
- [ ] Upgraded dress-up mermaid with AI-generated kawaii art and variant parts
- [ ] GitHub Pages deployment (static site, accessible on iPad)

### Future

- [ ] Scene builder: place customized mermaid into underwater scene backgrounds
- [ ] Print coloring pages: export/print uncolored outlines for real-world coloring
- [ ] Save creations: gallery of completed mermaids and colored pages
- [ ] Sound effects on interaction (tap, place, sparkle) with mute button
- [ ] Themed coloring page sets (Coral Reef, Mermaid Castle collections)

### Out of Scope

- Drawing / free canvas -- complexity too high, not the core ask
- Mini-games (matching, puzzles) -- not what she gravitates to in Crayola app
- App Store native app -- web app in Safari keeps it simple and fast to build
- Multiplayer / social -- this is a solo creative play experience
- User accounts / login -- she's 6, COPPA compliance is a legal minefield
- Cloud sync -- weekend-project-breaking complexity
- Complex color picker (HSL/hex) -- preset swatches work for a 6-year-old
- Zoom / pan -- spatial navigation is confusing for a child
- Onboarding tutorial -- if the app needs a tutorial, it's too complex
- Text input / labels -- a 6-year-old reads at beginner level

## Current Milestone: v1.1 Art & Deploy

**Goal:** Replace basic hand-crafted SVGs with AI-generated kawaii mermaid art, switch coloring to flood-fill, and deploy to GitHub Pages so she can use it on her iPad.

**Target features:**
- Automated art generation pipeline (OpenAI API + kawaii prompts + vtracer)
- AI-generated coloring pages with flood-fill interaction
- AI-generated dress-up mermaid with variant parts
- Static site deployment to GitHub Pages

## Context

Shipped v1.0 MVP with 2,172 LOC across Python, JavaScript, HTML, CSS.
Tech stack: FastAPI + vanilla JS, no framework, no build step.
SVG-first rendering with vtracer art pipeline for raster-to-SVG conversion.
37 Playwright E2E tests across 5 suites, all passing.
Two complete activities: dress-up (7 requirements) and coloring (4 requirements).
Platform: iPad Safari (web app).
Art style pivot: moving from watercolor filter on basic SVGs to kawaii-style AI-generated illustrations.

## Constraints

- **Audience**: Must be usable by a 6-year-old with zero instruction
- **Platform**: Must work well in Safari on iPad
- **Art style**: Consistent kawaii mermaid aesthetic across all assets
- **Scope**: Weekend-project scale -- keep it simple and fun

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Web app over native | Faster to build, no App Store, Python backend | Good -- shipped in 1 day |
| AI-generated art | No budget for commissioned art, faster iteration | Good -- watercolor SVGs look great |
| Watercolor style | Daughter's preference, dreamy mermaid aesthetic | Revisit -- pivoting to kawaii style for v1.1 |
| SVG-first rendering | Interactive regions, scalable, touch-friendly | Good -- enables dress-up and coloring |
| Vanilla JS, no framework | Weekend scope, no build step complexity | Good -- 893 LOC JS, fast iteration |
| vtracer for art pipeline | Raster-to-SVG conversion for future assets | Good -- works but PoC SVG was hand-crafted |
| SVG defs+use for variants | Single setAttribute to swap parts | Good -- clean, performant pattern |
| Pointer event delegation | Single listener, works on SVG regions | Good -- consistent touch handling |
| Duplicated COLORS array | Separate state lifecycles for dress-up and coloring | OK -- minor duplication, clear separation |
| Scene builder deferred to v2 | Weekend scope constraint | Pending |
| Print support deferred to v2 | Weekend scope constraint | Pending |

| Kawaii art style | User preference, cuter and more appealing for 6-year-old | -- Pending |
| Flood fill for coloring | Works with any AI-generated image, no manual region tagging | -- Pending |
| GitHub Pages deployment | Free static hosting, accessible on iPad anywhere | -- Pending |
| OpenAI API for art generation | Automate art pipeline, consistent kawaii style | -- Pending |

---
*Last updated: 2026-03-09 after v1.1 milestone start*
