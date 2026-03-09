# Domain Pitfalls

**Domain:** Kids creative web app (dress-up, coloring, scene builder) on iPad Safari
**Researched:** 2026-03-09
**Confidence:** MEDIUM (based on training data; web search tools unavailable for live verification)

---

## Critical Pitfalls

Mistakes that cause rewrites, broken core UX, or make the app unusable for a 6-year-old.

---

### Pitfall 1: Safari Touch Event Model Breaks Canvas Interaction

**What goes wrong:** Safari on iPad handles touch events differently from Chrome/Android. Key issues: (1) `touchmove` events don't fire unless `preventDefault()` is called on `touchstart`, but calling it also kills scrolling -- so you need to know *where* the touch started. (2) Safari has a 300ms click delay unless you add `touch-action: manipulation` CSS. (3) Double-tap zoom interferes with rapid tapping (selecting accessories). (4) Safari fires both touch events and synthesized mouse events, causing duplicate actions (e.g., selecting an accessory twice).

**Why it happens:** Developers test in Chrome DevTools with "mobile simulation" which uses mouse events, not real touch events. Everything works in dev, breaks on actual iPad.

**Consequences:** Coloring strokes lag or skip. Dress-up items get selected twice. Pinch-to-zoom unexpectedly fires when the child uses two fingers near the canvas. The child gets frustrated because tapping feels "broken."

**Prevention:**
- Use `pointer events` API (pointerdown/pointermove/pointerup) instead of separate touch/mouse handlers. Safari supports pointer events since iOS 13+.
- Add `touch-action: manipulation` on all interactive elements to kill the 300ms delay and disable double-tap zoom.
- Add `touch-action: none` on canvas/SVG areas where drawing happens.
- Test on a real iPad from day one -- not just Chrome DevTools.
- Set viewport meta: `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">` to prevent all zoom.

**Detection:** App works in browser dev tools but taps feel delayed, strokes skip, or items double-select on real iPad.

**Phase:** Must address in Phase 1 (foundation). Touch handling is the entire interaction model.

**Confidence:** HIGH -- these are well-documented Safari-specific behaviors.

---

### Pitfall 2: AI Art Style Inconsistency Across Generated Assets

**What goes wrong:** You generate mermaid tails with one prompt, hair with another, accessories with a third. Each generation has slightly different color palettes, line weights, shading styles, and proportions. A crown generated separately doesn't visually "belong" on a head generated in a different session. The watercolor aesthetic varies between "loose and blobby" and "tight and detailed" across assets.

**Why it happens:** AI image generators (DALL-E, Midjourney, Stable Diffusion) have no concept of a "style sheet." Each generation is probabilistic. Even with the same prompt prefix, outputs drift. The more separate generation sessions you run, the more divergent the assets become.

**Consequences:** The app looks like a collage of different artists instead of a cohesive product. A 6-year-old won't articulate "the style is inconsistent" but will feel something is "off" and lose the sense of magic.

**Prevention:**
- Generate assets in batches, not one-at-a-time. Generate all tails in one session, all hair in one session, etc.
- Use a single reference image in every generation prompt (img2img or style reference).
- Establish a strict prompt template with exact style descriptors: e.g., "watercolor, soft edges, pastel palette, no outlines, dreamy, on transparent background" -- reuse verbatim.
- Post-process all assets through the same pipeline: normalize brightness/contrast, apply consistent color grading, ensure uniform line weight.
- Consider generating "base" assets and then creating variations (recolors, flips) programmatically rather than generating each variant separately.
- For coloring pages specifically: generate the detailed version, then convert to outlines algorithmically (edge detection + threshold) rather than generating outlines separately. This ensures coloring pages match the dress-up assets.

**Detection:** Place two assets from different generation sessions side-by-side. If you can tell they came from different generations, the user can too.

**Phase:** Must address before any asset generation begins (Phase 1 or pre-Phase 1 asset pipeline setup). Fixing style inconsistency retroactively means regenerating everything.

**Confidence:** HIGH -- this is universally reported by developers using AI-generated assets.

---

### Pitfall 3: Canvas/SVG Performance Death on iPad Safari with Many Layers

**What goes wrong:** A dress-up feature stacks images: body base + tail + hair + crown + necklace + earrings + background scene + fish + coral + castle. Each layer is a high-resolution PNG with transparency. On an iPad (especially older models), compositing 10-15 large transparent PNGs on a canvas causes visible lag, jank when switching items, or outright crashes in Safari due to memory pressure.

**Why it happens:** Each transparent PNG must be alpha-composited. Safari's canvas implementation has lower memory limits than Chrome. iPads have 3-6 GB RAM shared between OS and all tabs. Safari aggressively kills tabs that use too much memory, with no warning -- the tab just reloads and the child loses her creation.

**Consequences:** Switching a hair style takes 500ms+. The app feels sluggish. Safari kills the tab silently, and when the child goes back, her mermaid is gone. Absolute worst case for a 6-year-old.

**Prevention:**
- Keep individual asset images small: 512x512px max per layer for dress-up pieces. The composite can be larger, but individual layers should be modest.
- Use SVG for dress-up components instead of raster PNGs. SVGs composite more efficiently, scale perfectly, and use far less memory. Recoloring is trivial (change fill attribute).
- If using canvas: render to an offscreen canvas only when something changes (not every frame). Cache the composite. Don't re-render on every touch.
- Flatten layers: when adding a new piece, composite the previous layers into a single cached image rather than re-compositing all layers from scratch.
- Monitor `performance.memory` (where available) or test on the oldest iPad you want to support.
- Limit total active layers to 8-10 maximum. If the design wants more, flatten background elements into a single image.

**Detection:** Test on an actual iPad (not Pro, ideally an iPad 9th gen or Air). If switching accessories isn't instant, there's a performance problem.

**Phase:** Architecture decision in Phase 1. Switching from canvas-PNG to SVG later is a full rewrite of the rendering system.

**Confidence:** HIGH -- canvas memory limits in Safari are well-documented and aggressively enforced.

---

### Pitfall 4: Touch Targets Too Small for a 6-Year-Old

**What goes wrong:** Developers (adults with fine motor skills using a mouse) design selection UI with reasonably sized buttons. On a real iPad, a 6-year-old's finger pad is ~15mm wide and their motor control is imprecise. They tap the crown but hit the necklace. They try to color inside a mermaid's tail but the brush paints outside. Frustration escalates fast.

**Why it happens:** Apple's HIG recommends 44pt minimum touch targets for adults. Kids need MORE, not less. Most developers follow adult guidelines and call it good.

**Consequences:** The child can't select what she wants. She gives up. The core value proposition -- "zero friction and pure delight" -- is broken.

**Prevention:**
- Minimum touch target: 60x60pt for all tappable elements. This is ~16mm physical, comfortable for a child's fingertip.
- Accessory/option selector: use a scrollable horizontal strip with large preview cards, not a grid of small thumbnails.
- Coloring tool: use a large brush size by default (20-30px radius). Provide only 2-3 size options (big, bigger, biggest), not a fine slider.
- Color picker: large swatches (at least 48x48pt each) in a single row or large grid. No color wheel -- a child cannot operate a color wheel.
- Drag-and-drop for scene building: make items snap to reasonable positions. Don't require pixel-perfect placement.
- Give generous hit areas: the tappable area should extend beyond the visible element by 8-10pt in all directions.

**Detection:** Watch a real 6-year-old use the app for 2 minutes. If she mis-taps more than once, the targets are too small.

**Phase:** Phase 1 UI/UX design. Retrofit is cheaper than most pitfalls but still wastes cycles.

**Confidence:** HIGH -- Apple HIG and child development research both support larger targets for children.

---

### Pitfall 5: Print-to-Color Pipeline Produces Bad Output

**What goes wrong:** The "print coloring page" feature is a key differentiator but has multiple failure modes: (1) The watercolor-style art doesn't convert cleanly to printable outlines -- soft edges become messy grey blobs. (2) Colors print instead of just outlines, wasting ink. (3) The printable area doesn't match paper proportions (iPad is 4:3, US letter is ~1.29:1, A4 is ~1.41:1). (4) Safari's print dialog adds headers/footers/margins that crop the image. (5) The outlines are too thin to see when printed, or too thick and look ugly.

**Why it happens:** Print CSS and screen CSS are completely different domains. Most web developers never deal with print. Safari's `window.print()` behavior has quirks (especially on iOS -- it opens a share sheet, not a print dialog). The watercolor aesthetic that looks beautiful on screen is specifically the hardest style to convert to clean outlines.

**Consequences:** Parent prints a coloring page and it looks terrible -- grey smudges, tiny on the paper, headers at the top. The "bridge between digital and physical" differentiator fails. If the parent has to fiddle with print settings, it's not "zero friction."

**Prevention:**
- Design coloring pages as a SEPARATE asset pipeline. Don't try to derive outlines from the watercolor art automatically. Generate clean vector outlines as the source-of-truth for coloring pages, then optionally add watercolor fills for the digital version.
- Use `@media print` CSS to: hide all UI chrome, force white background, set image to fill the page.
- Target 8.5x11" (US Letter) portrait as default layout. Add 0.5" margins on all sides for printer bleed.
- Test `window.print()` on actual iPad Safari. On iOS, this opens the system share sheet which allows AirPrint. Ensure the printable view is what gets captured.
- Alternative approach: generate a downloadable PDF instead of using browser print. This gives full control over layout. Python backend can generate PDFs with ReportLab or similar.
- Line weight for outlines: 2-3pt for main outlines, 1-1.5pt for detail lines. Test by actually printing.

**Detection:** Print a coloring page to a real printer. If a parent wouldn't hang it on the fridge, it needs work.

**Phase:** Dedicated phase for print pipeline. Don't leave this as "we'll add print later" -- the asset pipeline decision (vector outlines vs. raster conversion) must happen early.

**Confidence:** HIGH -- print CSS and Safari iOS print behavior are well-documented pain points.

---

## Moderate Pitfalls

---

### Pitfall 6: No Save/Restore Causes Lost Creations and Tears

**What goes wrong:** The child spends 10 minutes building her perfect mermaid. She accidentally swipes to go back in Safari, or the tab reloads (Safari aggressively reclaims memory), or the iPad goes to sleep and Safari drops the tab. Everything is gone.

**Prevention:**
- Auto-save state to `localStorage` on every meaningful change (item selection, color choice). Restore on page load.
- `localStorage` in Safari has a 5MB limit per origin. Store state as JSON references (which items are selected, which colors), not rendered images.
- For completed creations in the gallery: save the rendered composite as a data URL or Blob in `localStorage`, or save to the backend.
- Add `beforeunload` handler to warn about unsaved state (though Safari on iOS doesn't always honor this).
- Use the `visibilitychange` event to save state when the app goes to background.
- Test: open the app, build a mermaid, kill the Safari tab, reopen. The mermaid should still be there.

**Detection:** Kill Safari and reopen. If state is lost, this needs fixing.

**Phase:** Must be in Phase 1 or early Phase 2. Losing creations is emotionally devastating for the user.

**Confidence:** HIGH -- Safari tab lifecycle and localStorage behavior are well-documented.

---

### Pitfall 7: Overscoping the Weekend Project

**What goes wrong:** The project scope says "weekend project" but the feature list includes dress-up customization, scene builder, coloring pages, print support, gallery, and consistent watercolor art. This is easily 2-4 weeks of work if done properly. The developer either burns out trying to do everything, or ships a half-broken version of each feature instead of a polished version of one.

**Prevention:**
- Ruthlessly prioritize. The project description says the daughter loves Crayola Create and Play and the "core ask" is dress-up + coloring. Scene builder is additive.
- Phase 1 (weekend): Dress-up only. Pre-made set of 4-5 tails, 4-5 hair styles, 3-4 accessories. Tap to select. One background. Save screenshot. This alone will delight a 6-year-old.
- Phase 2 (next weekend): Add coloring pages. Start with 3-4 pre-made outline pages. Simple fill (tap region to color) rather than free-paint.
- Phase 3: Print support, scene builder, gallery.
- The watercolor art generation will take longer than the code. Budget 60% of time for asset creation/iteration, 40% for code.

**Detection:** If the first working demo isn't in the child's hands within 2 days, scope is too big.

**Phase:** Phase 0 (planning). Scope control is a planning-time decision.

**Confidence:** HIGH -- this is the most common failure mode for personal projects.

---

### Pitfall 8: Transparent PNG Background Handling on iPad

**What goes wrong:** AI-generated images come with backgrounds (usually white or a generated scene). Removing backgrounds to get transparent PNGs for layering is harder than expected. Automated background removal (rembg, remove.bg) leaves halos around soft watercolor edges. Semi-transparent watercolor washes lose their character when background-removed. The mermaid looks "cut out and pasted on" rather than naturally composited.

**Prevention:**
- Generate assets on a solid, unusual color background (e.g., bright green) that's easy to chroma-key out. Avoid white backgrounds since watercolor art often bleeds into white.
- Better: use SVG-based assets where transparency is native. Generate AI art as reference, then trace to SVG.
- If using PNGs: use `rembg` (Python library) for batch removal, then manually touch up the 10-15 most important assets. Don't try to automate everything.
- For coloring pages: outlines on white is fine -- no transparency needed since they print on white paper.
- Test compositing by layering a piece onto the actual background you'll use. Halo artifacts are immediately visible on non-white backgrounds.

**Detection:** Place a generated asset on a colored background. If there's a white fringe or halo around edges, the transparency extraction failed.

**Phase:** Phase 1 asset pipeline. Every phase that adds new assets will hit this problem if the pipeline isn't solved upfront.

**Confidence:** MEDIUM -- based on common AI art workflow reports in training data.

---

### Pitfall 9: Coloring "Flood Fill" Is Deceptively Hard

**What goes wrong:** The intuitive coloring interaction for a child is "tap a region, it fills with color" (like a paint bucket tool). Implementing flood fill on a canvas is simple in theory (BFS/DFS pixel walk) but has nasty edge cases: (1) anti-aliased outline edges cause color leaks -- the fill bleeds through semi-transparent pixels along lines. (2) Performance is poor on large regions on iPad -- a naive pixel-walk on a 1024x1024 canvas can freeze the UI for 1-2 seconds. (3) Undo is complex -- you need to store the previous pixel state.

**Why it happens:** Tutorials show flood fill on simple bitmaps with hard 1px edges. Real watercolor-style outlines have soft, anti-aliased, variable-width edges.

**Consequences:** Child taps to color the tail, and color bleeds through the outline into the background. Or the tap causes a visible freeze. She taps again thinking it didn't work, now she's queued multiple operations.

**Prevention:**
- Option A (simpler, recommended): Use SVG-based coloring pages with pre-defined regions as `<path>` elements. Tap a path, change its `fill` attribute. No pixel manipulation needed. Instant. No edge leaks. Trivially undoable.
- Option B: If using canvas flood fill, set a high tolerance threshold (40-60 on a 0-255 scale) to treat anti-aliased edge pixels as "wall" pixels. Use a scanline fill algorithm instead of recursive/BFS for performance. Run in a Web Worker to avoid blocking the UI.
- Option C: Pre-segment the coloring page into labeled regions (during asset creation). Store a "region map" -- a hidden canvas where each region is a unique solid color. Flood fill operates on the region map, not the visible art.
- For a weekend project, Option A (SVG paths) is the only realistic choice.

**Detection:** Try flood-filling a region in a watercolor-style outline. If color leaks through edges, the approach needs changing.

**Phase:** Phase 2 (coloring pages). The rendering approach decision (SVG vs. canvas) in Phase 1 directly determines what's possible here.

**Confidence:** HIGH -- flood fill edge-leak is one of the most commonly reported issues in coloring app development.

---

### Pitfall 10: Safari-Specific CSS and API Gaps

**What goes wrong:** Multiple small Safari-specific issues accumulate: (1) `position: fixed` behaves differently with the Safari toolbar -- bottom-fixed elements jump when the toolbar shows/hides. (2) CSS `backdrop-filter` (for blur effects) has intermittent rendering bugs in Safari. (3) `100vh` includes the Safari address bar height, so full-screen layouts have a scroll. (4) No native file-system save API -- `showSaveFilePicker()` doesn't exist in Safari, so "save image" requires a workaround. (5) `OffscreenCanvas` support was added only recently and may not work on older iPads.

**Prevention:**
- Use `100dvh` (dynamic viewport height) instead of `100vh` to account for Safari toolbar.
- For "save image": render to canvas, call `canvas.toBlob()`, create an `<a>` download link, or use the Web Share API (`navigator.share()`) which works well on iOS Safari.
- Avoid `position: fixed` for bottom-anchored toolbars. Use `position: sticky` or flex layout instead.
- Test every feature in Safari, not just Chrome. Use the iOS Safari Web Inspector (connected via Mac Safari > Develop menu) for debugging.
- If using `OffscreenCanvas`, check support with `typeof OffscreenCanvas !== 'undefined'` and fall back to regular canvas.

**Detection:** Test in Safari on iPad. Any layout that looks different from Chrome desktop is a Safari-specific issue.

**Phase:** Ongoing, but establish the viewport and layout foundations in Phase 1.

**Confidence:** HIGH -- Safari CSS quirks are very well-documented.

---

## Minor Pitfalls

---

### Pitfall 11: Color Palette Is Wrong for Watercolor Aesthetic

**What goes wrong:** The color picker offers standard saturated colors (fire-engine red, royal blue, bright yellow). These clash with the watercolor aesthetic which uses soft, muted, pastel tones. The child's colored creation looks garish against the soft background art.

**Prevention:**
- Curate a custom palette of 12-16 watercolor-appropriate colors: soft pink, lavender, seafoam, coral, sky blue, pale gold, etc.
- Name the colors with fun names the child will enjoy: "Mermaid Pink," "Ocean Sparkle," "Sunset Coral."
- Don't offer a free color picker. A curated palette prevents ugly results and is easier for a child to use.

**Detection:** Color a region and compare against the background art. If the colors feel jarring, the palette needs softening.

**Phase:** Phase 2 (coloring pages) but palette should be established during Phase 1 art direction.

**Confidence:** MEDIUM -- based on design best practices for children's apps.

---

### Pitfall 12: Gallery/Save Creates Storage Bloat

**What goes wrong:** Each saved creation stored as a data URL in `localStorage` is 100KB-500KB. After 20-30 saves (a prolific 6-year-old could do this in one session), `localStorage` hits the 5MB Safari limit. Subsequent saves silently fail. The gallery stops working.

**Prevention:**
- Store creation state as JSON metadata (selected items, colors) rather than rendered images. Re-render the preview from metadata when displaying the gallery.
- If storing images: compress heavily (JPEG quality 0.6 for gallery thumbnails, ~20KB each).
- Implement a gallery limit (e.g., 20 most recent) with oldest-first eviction.
- Monitor `localStorage` usage and warn (with a kid-friendly message) when approaching limits.
- Alternatively: use the backend to store gallery items, with creations keyed by a browser fingerprint or simple device ID.

**Detection:** Save 30 creations and check if the 31st save works.

**Phase:** Phase 2 or 3 (gallery feature).

**Confidence:** HIGH -- localStorage limits in Safari are well-documented (5MB per origin).

---

### Pitfall 13: Accidental Navigation Destroys State

**What goes wrong:** Safari has aggressive swipe-to-go-back gestures. A child painting on a canvas swipes horizontally to color a tail, and Safari interprets it as a back navigation. The page navigates away and the creation is lost.

**Prevention:**
- Build as a Single-Page Application. No navigation between pages means back-swipe has nowhere to go (after the initial page load).
- Alternatively, use `history.pushState()` to add entries so back-swipe triggers `popstate` event which you can intercept and use to show a "go back?" confirmation.
- Use `overscroll-behavior: none` CSS on the body to prevent pull-to-refresh (another accidental gesture).
- The canvas/interaction area should have `touch-action: none` to claim all touch gestures.

**Detection:** Swipe right on the canvas area. If Safari starts a back-navigation animation, this needs fixing.

**Phase:** Phase 1 (SPA architecture and touch event setup).

**Confidence:** HIGH -- Safari swipe navigation interference is a well-known issue for canvas apps.

---

### Pitfall 14: Asset Loading Time Creates Blank Stares

**What goes wrong:** If all mermaid assets (tails, hair, accessories, backgrounds, coloring pages) are loaded on app startup, the initial load takes 10+ seconds on a typical connection. The child sees a blank or loading screen and loses interest. If assets load lazily, switching to a new tail shows a flash of empty space.

**Prevention:**
- Preload the default/initial mermaid configuration (one body, one tail, one hair) on startup. Load the rest in the background.
- Use a fun loading animation (bubbles rising, a mermaid tail swishing) for the initial load. Keep it under 3 seconds for essential assets.
- Lazy-load alternative options with skeleton/shimmer placeholders in the selector strip.
- Optimize images: WebP format (Safari supports it since iOS 14), appropriate resolution (don't serve 2048px images for 200px display slots), use srcset.
- Consider inlining SVG assets in the HTML/JS bundle if using the SVG approach -- no additional network requests needed.

**Detection:** Throttle network to "Slow 3G" in dev tools. If any screen takes more than 3 seconds to become interactive, optimize.

**Phase:** Phase 1 (asset pipeline and loading strategy).

**Confidence:** MEDIUM -- standard web performance knowledge, specific thresholds for children based on general UX research.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation | Severity |
|-------------|---------------|------------|----------|
| Foundation/Setup | Safari touch event model (Pitfall 1) | Use pointer events, test on real iPad | Critical |
| Foundation/Setup | Accidental navigation (Pitfall 13) | SPA architecture, touch-action CSS | Critical |
| Asset Pipeline | AI art inconsistency (Pitfall 2) | Batch generation, style template, post-processing | Critical |
| Asset Pipeline | Transparent PNG halos (Pitfall 8) | Green-screen backgrounds or SVG approach | Moderate |
| Dress-Up Feature | Canvas/SVG performance (Pitfall 3) | SVG approach, layer limits, real-device testing | Critical |
| Dress-Up Feature | Touch targets too small (Pitfall 4) | 60pt minimum, test with actual child | Critical |
| Coloring Pages | Flood fill edge leaks (Pitfall 9) | SVG region-based fill, not pixel flood fill | Moderate |
| Coloring Pages | Color palette mismatch (Pitfall 11) | Curated pastel/watercolor palette | Minor |
| Print Feature | Print output quality (Pitfall 5) | Separate outline assets, PDF generation, test print | Critical |
| Save/Gallery | Lost creations (Pitfall 6) | Auto-save to localStorage on every change | Moderate |
| Save/Gallery | Storage bloat (Pitfall 12) | JSON metadata, not image blobs; eviction policy | Minor |
| Overall Scope | Weekend project overscope (Pitfall 7) | Phase 1 = dress-up only, resist feature creep | Moderate |
| Cross-cutting | Safari CSS quirks (Pitfall 10) | 100dvh, Web Share API, test in Safari always | Moderate |
| Cross-cutting | Asset loading time (Pitfall 14) | Preload essentials, lazy-load rest, optimize formats | Minor |

---

## Key Architectural Decision That Prevents Multiple Pitfalls

**SVG over Canvas for dress-up and coloring** is the single most impactful architectural choice. It simultaneously mitigates:

- **Pitfall 3** (performance): SVGs are lightweight and GPU-accelerated
- **Pitfall 8** (transparency): SVGs natively support transparency
- **Pitfall 9** (flood fill): SVG paths can be filled by changing attributes, no pixel manipulation
- **Pitfall 11** (recoloring): SVG fill/stroke attributes are trivially changeable
- **Pitfall 12** (storage): SVG state is compact JSON (which paths, which colors)

Canvas should only be used for the final "save as image" export (render SVG to canvas, then `toBlob()`).

---

## Sources

- Apple Safari Web Content Guide (touch event handling, viewport behavior) -- training data, not live-verified
- MDN Web Docs (Canvas API, Pointer Events, SVG) -- training data, not live-verified
- Apple Human Interface Guidelines (touch target sizing) -- training data, not live-verified
- Common patterns observed across children's app development discussions -- training data, not live-verified

**Note:** Web search and web fetch tools were unavailable during this research. All findings are based on training data (up to early 2025). Confidence levels reflect this limitation. The iPad Safari behaviors documented here are stable platform characteristics unlikely to have changed, supporting the assigned confidence levels despite the lack of live verification.
