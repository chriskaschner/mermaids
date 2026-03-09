# Feature Landscape

**Domain:** AI art generation pipeline, flood-fill coloring, dress-up art upgrade, static deployment for a children's creative app
**Researched:** 2026-03-09
**Milestone context:** v1.1 -- adding to an existing working app with SVG dress-up, region-based coloring, hash router, touch interactions

---

## Table Stakes

Features users expect. Missing = product feels incomplete or broken.

### AI Art Generation Pipeline

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| Consistent kawaii art style across all outputs | Mismatched art styles feel jarring; a 6-year-old notices when "mermaid looks different" | Med | Prompt engineering discipline | Use a locked system prompt with style anchors: "kawaii, chibi proportions, thick black outlines, pastel palette, no shading" |
| Clean line art for coloring pages (black outlines, white fill, no shading) | Coloring pages with gray blobs or crosshatching are unusable for tap-to-fill | Med | gpt-image-1 + post-processing | Prompt must explicitly say "no shading, no crosshatching, bold black outlines on white background." Real-world coloring book services confirm: AI frequently adds subtle gradients even when told not to. Post-processing cleanup required |
| Age-appropriate content filtering | Non-negotiable for a 6-year-old's app | Low | Server-side prompt wrapping | Append safety instructions to every prompt server-side. OpenAI models already filter, but belt-and-suspenders approach |
| Transparent background for dress-up parts | Parts must layer over each other without white rectangles showing through | Low | gpt-image-1 `background: "transparent"` + PNG output | Natively supported. Set quality to medium or high for clean transparency edges. Include "transparent background" in prompt as well -- model sets it automatically |
| Raster-to-SVG conversion via vtracer | Both coloring and dress-up use SVG for interaction; AI outputs raster images | High | vtracer pipeline (already exists in `src/mermaids/pipeline/trace.py`) | Existing pipeline handles this. Key tuning: coloring pages need `binary` colormode for clean outlines; dress-up parts need `color` colormode for multi-fill regions. Parameters `filter_speckle`, `color_precision`, `layer_difference` all affect output quality |
| Offline-first: pre-generated assets, no runtime API calls | A child opens the app on an iPad -- it must work instantly, no loading spinners waiting for an API | Low | Build-time pipeline | Pipeline runs at dev time, outputs committed as static SVG assets. Zero runtime dependency on OpenAI. This is the only sane architecture for a kids app |

### Flood Fill Coloring

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| Tap a region, it fills with selected color | Core coloring interaction. Must feel instant (< 100ms response) | High | Canvas-based flood fill replaces current SVG `data-region` fill | Current system: `pointerdown` -> find `[data-region]` ancestor -> `fillRegion()` changes fill on child paths. New system: render SVG to Canvas, flood fill from tap coordinates, pixel-level region detection. Eliminates manual region tagging entirely |
| Color palette with child-friendly presets | Already exists in v1.0 (10 swatches, `COLORS` array) | Low | Existing `COLORS` array in `coloring.js` | No change to palette needed. Only the fill mechanism changes |
| Undo (at least last action) | Already exists in v1.0 with closure-based undo stack | Med | Undo stack with canvas `ImageData` snapshots | Current closure-based undo (`pushUndo(() => { restore fills })`) won't work with canvas pixels. Must switch to snapshot-based: save full `getImageData()` before each fill operation. Memory cost: ~4MB per snapshot at 1024x1024. Cap at 15-20 undo steps |
| Anti-aliased edge handling with tolerance | AI-generated line art has anti-aliased edges. Naive exact-match flood fill either leaks through boundaries or leaves white halos around lines | High | Tolerance parameter (32-128 range for anti-aliased line art), tolerance fade for soft edges | FloodFill2D library solves this with `toleranceFade` -- applies alpha gradient at edges instead of hard cutoff. Without tolerance, fills look terrible on AI art. Tolerance too high = fill leaks through thin lines. Sweet spot requires per-image testing |
| Touch target tolerance | A 6-year-old taps imprecisely. Fill must work even when tap lands slightly off-target | Low | Inherent in flood fill algorithm | Flood fill naturally handles imprecise taps better than region-based: it fills whatever enclosed area the tap point lands in. No explicit accommodation needed |
| Works with any AI-generated image without manual tagging | The entire motivation for switching from region-based to flood fill | Med | Canvas rendering of SVG + pixel-based fill algorithm | Current system requires hand-crafted SVGs with `<g data-region="...">` groups (see `coloring.js:fillRegion()`). Flood fill works on any image with enclosed regions -- no manual tagging |

### Dress-Up with AI Art

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| Swappable parts (tail, hair, accessories) | Core dress-up mechanic, already working in v1.0 | Med | AI-generated part variants as SVG, placed in `<defs>`, swapped via `<use>` | Existing pattern: `PARTS = { tail: ["tail-1", "tail-2", "tail-3"], ... }`. Each `<use id="active-tail">` references `#tail-1`. `swapPart("tail", "tail-2")` changes the `href`. New SVGs must use same IDs |
| Color recoloring of active part | Already working in v1.0 by modifying fill on SVG path children | Med | SVG parts with fill-bearing `<path>` elements | `recolorActivePart()` calls `getFillBearingElements()` to find paths with `fill != "none"`, then sets new fill. vtracer output produces `<path>` elements with fills. This should work on traced SVGs, but need to verify vtracer's output structure matches expectations |
| Consistent character proportions across part variants | If tail-1 is 200px tall and tail-2 is 400px, the mermaid looks broken when swapping | High | Prompt engineering + post-processing normalization | Generate all variants at same canvas size with explicit size/proportion instructions in prompt. Post-generation: normalize viewBox, scale paths to consistent bounding box. This requires manual adjustment |
| Parts align at connection points (hair sits on head, tail connects to body) | Without alignment, swapping parts produces a Frankenstein mermaid | High | SVG viewBox alignment, consistent anchor positioning across all variants | Hardest integration problem in v1.1. AI won't naturally produce parts that align at connection points. Strategy: generate each part against a reference silhouette/template. Post-process to align anchor points. Expect manual SVG editing |
| Celebration on completion | Sparkle effect when all categories customized. Already works in v1.0 | Low | Existing `checkCompletion()` + `triggerCelebration()` in `dressup.js` and `sparkle.js` | No change needed. Carries over automatically |

### GitHub Pages Deployment

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| App loads at GitHub Pages URL | The whole point -- she can open it on her iPad from anywhere | Low | Static files served from repo, Pages enabled in repo settings | Hash router (`#/home`, `#/dressup`, `#/coloring`) already avoids the SPA 404 problem. GitHub Pages returns 404 for frontend routes like `/dressup`, but hash routes (`#/dressup`) never hit the server |
| `.nojekyll` file in deploy root | Without it, Jekyll processing may interfere with file serving | Low | Empty file at repo root | Current project has no underscore-prefixed files, but add `.nojekyll` defensively. Jekyll can cause subtle issues with ES module serving |
| ES modules work correctly | App uses `<script type="module" src="js/app.js">` with `import`/`export` statements | Low | GitHub Pages serves `.js` with correct MIME type | Verified: GitHub Pages serves JavaScript files correctly. ES modules with relative imports work fine |
| No server dependency for static serving | Currently uses FastAPI (`app.py`) to serve static files. GitHub Pages is static-only | Med | Replace absolute asset paths, make FastAPI optional | Critical: `renderDressUp()` fetches `"/assets/svg/mermaid.svg"` with absolute path. On GitHub Pages at `username.github.io/mermaids/`, this resolves to `username.github.io/assets/svg/mermaid.svg` (wrong). Must use relative paths `"./assets/svg/mermaid.svg"` or `"assets/svg/mermaid.svg"` |
| Works on iPad Safari | Primary target platform | Low | Already handled in v1.0 | Existing meta tags: `apple-mobile-web-app-capable`, `viewport-fit=cover`, `user-scalable=no`. Pointer event handling already works. No changes needed |

---

## Differentiators

Features that add delight beyond the baseline. Not expected, but valued.

| Feature | Value Proposition | Complexity | Dependencies | Notes |
|---------|-------------------|------------|--------------|-------|
| Preprocessed instant flood fill via Web Worker | Standard flood fill takes 100-500ms per tap on large canvases. Preprocessing assigns each enclosed region a unique ID on page load, making subsequent fills instant (< 10ms). KidzFun.art uses this approach | High | Web Worker for background preprocessing, alpha-channel region mapping | Preprocessing assigns incremental alpha values (1-255) to each enclosed area. On tap: look up alpha value, apply color mask using `globalCompositeOperation = "source-in"`. Limit: 255 regions per image. Only pursue if standard fill is noticeably slow on iPad |
| Sparkle feedback on each coloring fill | Existing sparkle system in `sparkle.js` only triggers on dress-up completion. Triggering a small burst at the tap point on each fill gives immediate tactile delight | Low | Existing `triggerCelebration()` or lighter-weight burst variant | Low effort, high delight. Trigger a 3-5 particle burst at touch coordinates on fill |
| PWA with "Add to Home Screen" | iPad Safari already supports `apple-mobile-web-app-capable` (meta tag present). Full PWA manifest + icons makes it feel like a "real app" on her home screen | Med | `manifest.json`, service worker for offline caching, app icons at multiple sizes | Service worker could cache all SVG assets for fully offline use. Would survive airplane mode / no wifi scenarios |
| Clear/reset coloring page | "Start over" button resets all fills to original line art | Low | Redraw original SVG to canvas, clear undo stack | Simple: keep original SVG source, re-render to canvas on reset |
| Animated view transitions | Smooth fade or slide when navigating between home/dressup/coloring | Med | CSS transitions or `View Transitions API` on view swap | Current implementation sets `innerHTML` directly (instant, jarring). Polish feature, not critical |

---

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Runtime AI image generation (generate on user request) | 10-30 seconds per image (gpt-image-1), requires API key in client-side code, costs ~$0.07/image, requires network. A 6-year-old will not wait 30 seconds | Pre-generate all assets at build time using Python pipeline. Commit SVGs as static assets |
| Free-draw / paintbrush tool | Massive complexity: brush engine, pressure sensitivity, layer management, eraser. Out of scope per PROJECT.md | Keep flood fill as the only coloring interaction. Tap-to-fill is the model |
| Complex color picker (HSL wheel, hex input) | A 6-year-old cannot use a color wheel. Out of scope per PROJECT.md | Keep 10 preset swatches. Big colored circles to tap |
| Save/export/share colored pages | Canvas-to-image conversion, download handling, sharing API. Scope creep for v1.1 | Defer to v2 (listed in PROJECT.md Future section) |
| User-customizable prompts for AI generation | A 6-year-old cannot type prompts. Adds content moderation complexity | All prompts are developer-authored and locked in the pipeline |
| Multiple character bases for dress-up | One mermaid base is enough. Multiple bases multiplies the part alignment problem | One base, multiple variants per category (3 tails, 3 hairs, 3+ accessories) |
| Zoom/pan on coloring pages | Spatial navigation confusing for a child. Out of scope per PROJECT.md | Design coloring pages at a scale that fills the iPad screen without needing zoom |
| Backend API for the deployed app | FastAPI is currently the server. GitHub Pages cannot run Python. Do not try to add a serverless backend for v1.1 | The deployed app is 100% static. Python pipeline runs locally at dev time only |

---

## Feature Dependencies

```
AI Art Pipeline (Python, build-time only)
  |
  |---> generates coloring page PNGs (black outlines, white background)
  |       |
  |       |---> vtracer converts to SVG (binary mode, clean outlines)
  |               |
  |               |---> SVG rendered to <canvas> for flood fill interaction
  |
  |---> generates dress-up part PNGs (transparent background, color regions)
          |
          |---> vtracer converts to SVG (color mode, preserves fill regions)
                  |
                  |---> SVG placed in <defs>, swapped via <use> (existing pattern)

Flood Fill (replaces region-based coloring in coloring.js)
  |
  |---> REQUIRES: Canvas-based rendering (architectural shift from pure SVG DOM)
  |---> REQUIRES: Flood fill algorithm with tolerance (for anti-aliased edges)
  |---> REQUIRES: New undo strategy (ImageData snapshots, not closure-based)
  |---> BREAKS: Current pointerdown -> closest("[data-region]") -> fillRegion() flow
  |---> PRESERVES: Color palette (COLORS array), page gallery, back button, undo UX

Dress-Up Art Upgrade
  |
  |---> REQUIRES: AI-generated SVGs placed in <defs> with IDs matching PARTS config
  |---> REQUIRES: Part alignment (viewBox consistency, anchor point matching)
  |---> PRESERVES: swapPart(), recolorActivePart(), initDressUp(), category tabs
  |---> PRESERVES: checkCompletion(), triggerCelebration()
  |---> UPDATE NEEDED: getVariantPreviewSVG() (new thumbnails for new art)

GitHub Pages Deployment
  |
  |---> REQUIRES: Fix absolute paths ("/assets/...") to relative ("./assets/...")
  |---> REQUIRES: .nojekyll file at repo root
  |---> REQUIRES: FastAPI becomes optional (dev-only convenience, not required)
  |---> PRESERVES: Hash router (already GitHub Pages compatible)
  |---> PRESERVES: ES module script loading, all meta tags
```

---

## MVP Recommendation

Prioritize in dependency order:

1. **AI Art Generation Pipeline** -- everything else depends on having assets
   - Use gpt-image-1 at medium quality (~$0.07/image, 1024x1024)
   - Generate ~4 coloring page line art images (black outlines, white background, kawaii mermaid themes)
   - Generate ~9 dress-up part variants (3 tails, 3 hairs, 3 accessories) with transparent backgrounds
   - Estimated cost: ~13 images x $0.07 x 3-5 iteration runs = $3-5 total
   - Lock a system prompt template for style consistency across all generations

2. **vtracer SVG Conversion** -- convert AI raster output to interactive SVGs
   - Coloring pages: `binary` colormode, `filter_speckle=20`, clean black/white outlines
   - Dress-up parts: `color` colormode, `filter_speckle=10`, preserve fill-bearing regions
   - Pipeline already exists in `trace.py` -- extend with coloring-specific vs dress-up-specific parameter sets

3. **Flood Fill Coloring** -- replace region-based system with canvas flood fill
   - Render SVG coloring page onto `<canvas>` element
   - Implement iterative (stack-based, not recursive) flood fill with tolerance ~64-128
   - Use `toleranceFade` for anti-aliased edge handling
   - Canvas `ImageData` snapshot undo (replacing closure-based undo)
   - Overlay original SVG outlines on top of canvas for crisp line rendering at any resolution
   - Test on iPad Safari for performance before considering Web Worker preprocessing

4. **Dress-Up Art Integration** -- swap hand-crafted SVGs for AI-generated ones
   - Place new traced SVGs into `<defs>` with IDs matching `PARTS` config (`tail-1`, `tail-2`, etc.)
   - Verify `recolorActivePart()` works with vtracer-output path elements
   - Align parts using consistent viewBox dimensions (normalize all to same coordinate space)
   - Update `getVariantPreviewSVG()` with new preview thumbnails

5. **GitHub Pages Deployment** -- make it accessible on iPad
   - Add `.nojekyll` to repo root
   - Change all absolute paths to relative (`"/assets/svg/mermaid.svg"` -> `"assets/svg/mermaid.svg"`)
   - Enable GitHub Pages on `main` branch, publish from root or `/frontend` directory
   - Verify on iPad Safari at deployed URL

**Defer:**
- Preprocessed instant fill (Web Worker): only if standard flood fill is too slow on iPad
- PWA manifest / service worker: nice-to-have, not blocking v1.1
- Animated view transitions: polish, not substance
- Print support: listed in PROJECT.md Future, not in v1.1 scope

---

## Complexity Assessment

| Feature Area | Effort | Risk | Notes |
|--------------|--------|------|-------|
| AI prompt engineering for consistent kawaii art | Medium | Medium | Iteration-heavy. Expect 3-5 generation runs per asset. AI line art often includes unwanted shading despite prompt instructions |
| vtracer parameter tuning | Medium | Low | Pipeline exists and works. Tuning `filter_speckle`, `color_precision`, `layer_difference` is incremental trial-and-error |
| Flood fill implementation | High | High | Architectural shift from SVG DOM manipulation to Canvas pixel operations. Undo system rewrite. Anti-aliasing tolerance tuning. iPad Safari canvas performance is the unknown |
| Dress-up part alignment | High | High | AI-generated parts will NOT naturally align at connection points. Manual SVG editing almost certainly required. This is the single hardest integration problem |
| GitHub Pages deployment | Low | Low | Hash router eliminates the hard SPA routing problem. Mostly find-and-replace on asset paths |

---

## Sources

- [OpenAI Image Generation API docs](https://developers.openai.com/api/docs/guides/image-generation/) -- HIGH confidence
- [OpenAI Cookbook: Generate images with GPT Image](https://developers.openai.com/cookbook/examples/generate_images_with_gpt_image/) -- HIGH confidence
- [GPT Image 1 Model docs](https://developers.openai.com/api/docs/models/gpt-image-1) -- HIGH confidence
- [GPT Image 1.5 Model docs](https://platform.openai.com/docs/models/gpt-image-1.5) -- HIGH confidence
- [OpenAI API Pricing](https://openai.com/api/pricing/) -- HIGH confidence
- [KidzFun.art: Using DALL-E for kids coloring pages](https://shaneosullivan.wordpress.com/2024/04/09/using-dall-e-ai-to-create-kids-colouring-pages-in-kidzfun-art/) -- MEDIUM confidence
- [Instant colour fill with HTML Canvas (Web Worker preprocessing)](https://shaneosullivan.wordpress.com/2023/05/23/instant-colour-fill-with-html-canvas/) -- MEDIUM confidence
- [FloodFill2D library (tolerance + anti-aliasing)](https://github.com/blindman67/FloodFill2D) -- HIGH confidence (direct source code)
- [floodfill.js (basic canvas flood fill)](https://github.com/binarymax/floodfill.js/) -- HIGH confidence (direct source code)
- [Canvas flood fill that doesn't kill the browser](https://ben.akrin.com/an-html5-canvas-flood-fill-that-doesnt-kill-the-browser/) -- MEDIUM confidence
- [HN: Personalized coloring book with OpenAI image API](https://news.ycombinator.com/item?id=43791992) -- MEDIUM confidence
- [GitHub Pages SPA routing discussion](https://github.com/orgs/community/discussions/64096) -- HIGH confidence
- [vtracer repository](https://github.com/visioncortex/vtracer) -- HIGH confidence (direct source)
- [GitHub Pages and Jekyll docs](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll) -- HIGH confidence
