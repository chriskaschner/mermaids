# Feature Landscape

**Domain:** Kids creative activity app (dress-up, coloring, scene builder) for a 6-year-old
**Researched:** 2026-03-09
**Confidence:** MEDIUM -- based on training data knowledge of Crayola Create and Play, Toca Boca, and kids app design patterns through mid-2025. Web verification was unavailable.

## Competitive Landscape Context

The kids creative app space breaks into three tiers:

1. **Premium subscription apps** (Crayola Create and Play, Toca Boca Days): 100+ activities, frequent content updates, $5-8/month, large studios
2. **Focused free/paid apps** (individual dress-up or coloring apps): 1-2 activities done well, ad-supported or $3-5 one-time, small studios
3. **Web-based toys** (PBS Kids games, educational sites): lightweight, browser-based, narrow scope

This project fits squarely into tier 3 -- a focused web-based toy. Feature list below is calibrated to that tier: do 2-3 things well for one kid, not 50 things for the App Store.

---

## Table Stakes

Features a 6-year-old expects after using apps like Crayola Create and Play. Missing these means the app feels broken or boring, not "simple."

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Drag-and-drop dress-up** | Core mechanic of every dress-up app. Tap an option, it appears on the mermaid. | Medium | SVG `<use>` elements swapped on tap. Accessories draggable via pointer events. Minimum 3-4 options per category (tails, hair, crowns, accessories). |
| **Instant visual feedback** | Kids expect things to happen the moment they tap. Zero loading, zero delays. | Low | SVG attribute changes are instant. No server round-trips for any interactive action. |
| **Color selection for customization** | Every dress-up app lets kids pick colors. A fixed set of items with no color choice feels rigid. | Low | 8-12 color swatches. Tap swatch -> SVG `fill` attribute changes on the selected part. No color picker widget. |
| **Tap-to-fill coloring** | Tap a region, it fills with color. Standard kids coloring app interaction. | Medium (asset prep), Low (code) | SVG regions as `<path>` elements. Tap path -> change `fill`. Pre-segmented SVG pages require upfront asset work but make the code trivial. |
| **Undo button** | Kids constantly tap wrong things. One big undo button. | Low | State stack. Pop last state, restore SVG attributes. |
| **Big, obvious tap targets** | A 6-year-old's motor control requires 44pt minimum. 60pt is better. | Low | Design constraint, not a feature to build. All buttons, swatches, and interactive elements must be large. |
| **Clear navigation between activities** | Kids need to know "I can do dress-up" and "I can do coloring" without reading. Icons, not text. | Low | Bottom tab bar or large visual buttons on home screen. Maximum 3-4 destinations. Icons only. |
| **Gallery / save creations** | "Look what I made!" is the entire payoff. Kids revisit their gallery obsessively. | Medium | SVG state serialized as JSON -> localStorage. Thumbnails generated via SVG->Canvas->PNG export. |
| **Sound effects on interaction** | Every kids app has tap sounds, swooshes, sparkle effects. Silence feels broken. | Low | Short audio clips. Web Audio API with user-gesture unlock for iOS Safari. Provide mute button for parents. |
| **Consistent art style** | Mixing styles looks cheap. Kids apps live or die on visual cohesion. | N/A (asset production) | All AI-generated assets must share the same watercolor aesthetic. Asset pipeline concern. |

---

## Differentiators

Features that set this app apart from generic dress-up/coloring apps. Not expected, but they create delight.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Print coloring pages** | Bridges digital and physical play. Most coloring apps are digital-only. A 6-year-old coloring on paper with real crayons after choosing her page digitally -- that is magic. | Low | SVG outlines print crisply at any DPI. CSS `@media print` + `window.print()`. This is the #1 differentiator per PROJECT.md. |
| **Scene builder with placed mermaid** | Dress-up apps stop at "here's your character." Scene builders let kids place their character into a world. | High | Place customized mermaid into underwater scenes. Add scene elements (fish, coral, treasure). Reuses dress-up SVG mechanics. Most complex feature. |
| **Watercolor art style** | Most kids apps use flat vector or glossy 3D. A soft, dreamy watercolor aesthetic is rare and memorable. | N/A (asset production) | Visual identity differentiator. Must be consistent and high quality. |
| **Animation on completion** | Sparkles when all slots filled, bubbles when coloring page is finished. Creates a "ta-da!" moment. | Low-Medium | CSS animation or SVG SMIL. 2-3 seconds. Do not block interaction. |
| **Themed coloring page sets** | Groups like "Coral Reef Collection," "Mermaid Castle Collection." Gives a sense of collection. | Low | Purely organizational. 3-4 sets of 3-4 pages each. |
| **Stamp tool** | Pre-made stamps (stars, shells, fish) to decorate scenes. | Low | Same as dress-up accessories -- SVG elements placed on canvas. |

---

## Anti-Features

Features to explicitly NOT build. Each is a trap that seems valuable but would blow up scope, confuse a 6-year-old, or undermine the core experience.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Free drawing / canvas painting** | High complexity (undo, brushes, eraser, performance). Touch drawing on iPad is imprecise for a 6-year-old. Drawing apps are their own product category. | Stick to tap-to-fill coloring (SVG regions) and dress-up (pick from options). Constraint enables creativity for this age group. |
| **Mini-games (matching, puzzles)** | Not what the target user gravitates to per PROJECT.md. Splits development effort across unrelated mechanics. | Keep all activities creative/expressive. No scoring, no timers, no win/lose. |
| **User accounts / login** | She is 6. Auth is friction. COPPA compliance is a legal minefield for a weekend project. | Use localStorage. Anonymous by design. |
| **Cloud sync** | Requires database, user identity, conflict resolution. Weekend-project-breaking complexity. | Local-only saves. If data is lost, she makes new mermaids. |
| **Sharing / social** | COPPA, moderation, abuse risk. Social features for kids under 13 require legal compliance infrastructure. | "Sharing" means showing the iPad to a parent, or printing a page. |
| **In-app text / reading required** | A 6-year-old reads at a beginner level. Any feature requiring reading instructions will fail. | All navigation via icons. All interaction via direct manipulation. Zero required reading. |
| **Complex layer management** | Photoshop-style layers, z-ordering controls. Way beyond a child's mental model. | Auto-layer management. SVG element order handles z-ordering. User never sees or manages layers. |
| **Complex color picker** | HSL sliders, hex input, color wheel. Too complex for a 6-year-old. | Fixed palette of 12-16 preset colors. Big colored circles to tap. |
| **Zoom / pan on canvas** | Spatial navigation is confusing for a child. | Fixed viewport. Design SVG viewBox to fill iPad screen. |
| **Premium content / IAP** | This is for one kid. No business model. | Everything unlocked from day one. |
| **Onboarding tutorial** | If the app needs a tutorial, the app is too complex. Kids skip tutorials immediately. | The biggest, most colorful thing on screen should be the thing to tap. |
| **Animation / video creation** | "Make your mermaid swim!" is a full animation tool. Months of work. | Static compositions. Subtle idle animations (hair floating, tail swaying) are decorative, not user-created. |
| **Text labels or names** | Requires keyboard input. A 6-year-old typing is slow and frustrating. | Gallery shows visual thumbnails only. No names. |

---

## Feature Dependencies

```
Art Assets (generated SVGs) --> Dress-Up (needs mermaid part SVGs)
Art Assets (generated SVGs) --> Scene Builder (needs background images)
Art Assets (generated SVGs) --> Coloring Pages (needs pre-segmented SVG outlines)

Dress-Up --> Scene Builder (scene builder places the dressed-up mermaid)
Coloring Pages --> Print (prints the coloring page, colored or outline)

Dress-Up --> Save to Gallery (saves assembled mermaid state)
Scene Builder --> Save to Gallery (saves scene state)
Coloring Pages --> Save to Gallery (saves colored page state)

Sound Effects --> All interactive screens (independent, can add to any screen)
Navigation --> All screens (home screen routes to each activity)
```

**Critical path:** Art Assets -> Navigation -> Dress-Up -> Scene Builder -> Gallery.
Coloring pages are independent of dress-up and can be built in parallel after the art asset pipeline.

---

## MVP Recommendation

**Phase 1 -- "She can play with it":**

1. **Dress-up with color selection** -- Core mechanic. Swappable tails, hair, and 3-4 accessories in selectable colors. This alone provides 30+ minutes of play.
2. **Coloring pages with tap-to-fill** -- Independent second activity. 4-6 pre-segmented SVG coloring pages. Tap region, pick color.
3. **Print coloring pages** -- The signature differentiator. Low code complexity (CSS print + `window.print()`).
4. **Basic navigation** -- Home screen with 2-3 big icon buttons.
5. **Sound effects** -- 5-6 audio clips (tap, place, sparkle, splash). Tiny effort, massive feel improvement.

**Phase 2 -- "It feels complete":**

6. **Gallery / save creations** -- Persist dressed-up mermaids and colored pages. Revisit and admire.
7. **Scene builder** -- Place dressed-up mermaid in underwater scenes. Most complex feature, benefits from dress-up being solid first.
8. **Celebration animations** -- Sparkles, bubbles. Polish layer.

**Defer (Phase 3 or never):**

- **Stamp tool** -- Easy to add later. Same SVG pattern as accessories.
- **Themed coloring page sets** -- Needs 12+ pages to justify grouping.
- **Free brush painting** -- Only if SVG region coloring feels too limiting. Requires Canvas, much more complex.

---

## Complexity Budget Reality Check

This is a weekend project. Total complexity budget is roughly:

| Feature | Estimated Effort | Cumulative |
|---------|-----------------|------------|
| Art asset pipeline (AI generation + SVG prep) | 6-10 hours | 6-10 hours |
| Dress-up (core mechanic + colors) | 3-5 hours | 9-15 hours |
| Coloring pages (SVG region fill) | 2-4 hours | 11-19 hours |
| Print support | 1 hour | 12-20 hours |
| Navigation + app shell | 1-2 hours | 13-22 hours |
| Sound effects | 1 hour | 14-23 hours |
| Gallery / save | 2-3 hours | 16-26 hours |
| Scene builder | 4-8 hours | 20-34 hours |

**The art asset pipeline is the hidden time sink.** Every dress-up option needs an SVG. Every coloring page needs pre-segmented regions. Every scene needs a background. Budget at least as much time for asset creation/curation as for code.

**Scene builder may need to be Phase 2 or a stretch goal.** Dress-up + coloring + print is a complete, delightful experience on its own. The app works without scenes.

---

## Sources

- Crayola Create and Play app features (training data knowledge, MEDIUM confidence)
- Toca Boca series feature patterns (training data knowledge, MEDIUM confidence)
- Apple Human Interface Guidelines for kids apps (training data knowledge, HIGH confidence on touch targets)
- COPPA compliance requirements (training data knowledge, HIGH confidence -- established law)
- PROJECT.md requirements and constraints (direct source, HIGH confidence)
