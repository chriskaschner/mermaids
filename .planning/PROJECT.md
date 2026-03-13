# Mermaid Create & Play

## What This Is

A web-based creative activity app for a 6-year-old, themed entirely around mermaids. Two activities: dress-up (mix and match AI-generated kawaii mermaid parts with color customization) and coloring (canvas flood-fill on AI-generated mermaid pages with crisp SVG overlays). Live at mermaids.chriskaschner.com, designed for iPad Safari with 60pt+ touch targets and zero-instruction usability.

## Core Value

A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages -- with zero friction and pure delight.

## Requirements

### Validated

- [x] Mermaid dress-up: mix and match tail colors, hair styles, crowns, and accessories -- v1.0
- [x] Coloring pages: mermaid-themed outlines to color digitally -- v1.0
- [x] Watercolor art style: dreamy, soft, painterly visual aesthetic throughout -- v1.0
- [x] Touch-friendly: designed for iPad touch interaction, big tap targets, no tiny UI -- v1.0
- [x] AI art generation pipeline (OpenAI API + kawaii mermaid prompts + vtracer tracing) -- v1.1
- [x] Upgraded coloring pages with AI-generated art and flood-fill interaction -- v1.1
- [x] Upgraded dress-up mermaid with AI-generated kawaii art and variant parts -- v1.1
- [x] GitHub Pages deployment (static site, accessible on iPad) -- v1.1

### Active

## Current Milestone: v1.2 Mermaid Art Rework

**Goal:** Fix dress-up and coloring art so both use a single base mermaid with swappable parts (hair, eyes, tail) and closed hair regions for paint bucket.

**Target features:**
- Dress-up rework: one base mermaid with swappable hair, eyes, and tail (not different mermaids per item)
- Coloring rework: coloring pages with hair/eyes/tail variety (not just accessories)
- Closed hair regions: hair shapes are filled/closed so flood-fill works on them

### Future

- [ ] Scene builder: place customized mermaid into underwater scene backgrounds
- [ ] Print coloring pages: export/print uncolored outlines for real-world coloring
- [ ] Save creations: gallery of completed mermaids and colored pages
- [ ] Sound effects on interaction (tap, place, sparkle) with mute button
- [ ] Themed coloring page sets (Coral Reef, Mermaid Castle collections)
- [ ] Dress-up-to-coloring: the mermaid you customize in dress-up becomes the coloring page you color

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

## Context

Shipped v1.1 with 5,382 LOC across Python, JavaScript, HTML, CSS.
Tech stack: vanilla JS frontend (no framework, no build step), Python pipeline for AI art generation.
SVG-first rendering with OpenAI gpt-image-1 + vtracer art pipeline.
62 Playwright E2E tests across multiple suites (60 passing, 2 pre-existing WebKit sparkle failures).
Two complete activities: dress-up (AI-generated kawaii art, 9 variants, color recoloring) and coloring (canvas flood fill, SVG overlay, undo).
Platform: iPad Safari via GitHub Pages (mermaids.chriskaschner.com).
CI/CD: GitHub Actions with E2E test gate before deploy.
Art style: kawaii flat-color mermaid illustrations (pivoted from watercolor in v1.0).

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
| Watercolor style | Daughter's preference, dreamy mermaid aesthetic | Revisit -- pivoted to kawaii style for v1.1 |
| SVG-first rendering | Interactive regions, scalable, touch-friendly | Good -- enables dress-up and coloring |
| Vanilla JS, no framework | Weekend scope, no build step complexity | Good -- 893 LOC JS, fast iteration |
| vtracer for art pipeline | Raster-to-SVG conversion for future assets | Good -- works for both hand-crafted and AI-generated |
| SVG defs+use for variants | Single setAttribute to swap parts | Good -- clean, performant pattern |
| Pointer event delegation | Single listener, works on SVG regions | Good -- consistent touch handling |
| Kawaii art style | User preference, cuter and more appealing for 6-year-old | Good -- AI-generated kawaii parts look cohesive |
| Flood fill for coloring | Works with any AI-generated image, no manual region tagging | Good -- eliminates manual SVG region prep |
| GitHub Pages deployment | Free static hosting, accessible on iPad anywhere | Good -- live at custom domain with HTTPS |
| OpenAI API for art generation | Automate art pipeline, consistent kawaii style | Good -- 9 variant parts + 4 coloring pages generated |
| Canvas+SVG hybrid for coloring | Canvas for flood fill, SVG overlay for crisp lines | Good -- retina-quality outlines with pixel-level fill |
| Edit API with masks for variants | Consistent spatial alignment across generated parts | Good -- all 9 variants fit within 400x700 viewBox |
| z-index + stopPropagation for iPad | iOS Safari fixed-position layering quirk | Good -- resolved touch interaction issues on live site |
| CI test gate before deploy | Prevent broken builds from reaching production | Good -- caught real issues |

---
*Last updated: 2026-03-12 after v1.2 milestone start*
