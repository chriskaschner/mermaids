# Domain Pitfalls

**Domain:** AI-generated art pipeline + flood-fill coloring + static deployment for kids' creative app
**Researched:** 2026-03-09
**Context:** v1.1 milestone -- adding AI art, flood fill, dress-up decomposition, GitHub Pages to existing v1.0 app

---

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

---

### Pitfall 1: Flood Fill Cannot Work on SVG DOM -- Requires Canvas Layer

**What goes wrong:** The v1.0 coloring system uses `data-region` groups with `setAttribute("fill", color)` on SVG `<g>` elements. This is region-based coloring, not flood fill. Flood fill is a pixel-level algorithm that requires `getImageData()` on a canvas. You cannot implement flood fill by manipulating SVG DOM attributes. Traced SVGs from AI art will not have clean, semantically-labeled `<g data-region>` groups -- they are just raw `<path>` elements with no semantic meaning.

**Why it happens:** The v1.0 system works beautifully because coloring page SVGs were hand-crafted with named `data-region` groups (see `page-1-ocean.svg`: `<g data-region="tail">`, `<g data-region="hair">`, etc.). The temptation is to keep this approach and just "auto-detect" regions from traced SVGs, but traced SVGs have hundreds of overlapping stacked paths with no semantic grouping.

**Consequences:** If you try to implement flood fill as SVG attribute manipulation, you either (a) need to manually tag every traced path with `data-region` (defeating the purpose of AI generation), or (b) accept that tapping fills only a single tiny path fragment under the pointer, which looks broken to a 6-year-old who expects a whole tail to fill.

**Prevention:**
- Accept that flood fill means adding a **canvas-based rendering layer** for coloring pages
- Architecture: render the SVG line art onto a hidden `<canvas>`, run flood fill on the canvas pixel data via `getImageData()`/`putImageData()`, display the canvas as the visible coloring surface
- Keep SVG as the source format (scalable, clean lines) but use canvas for user interaction
- Alternatively: use SVG line art as a crisp overlay on top of the canvas fill layer (best of both worlds)

**Detection:** If your flood fill implementation never calls `getImageData()` or `putImageData()`, it is not a flood fill -- it is region-based coloring with extra steps.

**Impact on existing code:**
- `coloring.js` `fillRegion()` function (which does `element.setAttribute("fill", color)`) cannot be used for flood fill on traced SVGs
- `app.js` coloring page touch handler (`event.target.closest("[data-region]")`) will not work on canvas -- canvas has no child elements to traverse
- The undo system (storing previous fill values) needs to change to storing canvas image snapshots or pixel diffs

**Confidence:** HIGH -- canvas flood fill is a well-established pattern with many reference implementations (q-floodfill, FloodFill2D).

---

### Pitfall 2: vtracer Color-Mode Output Produces Hundreds of Paths That Kill iPad Performance

**What goes wrong:** vtracer in `color` mode with `hierarchical="stacked"` traces every color region in an AI-generated image as a separate `<path>`. A kawaii mermaid illustration with gradients, shading, and detail easily produces 200-500+ paths. The v1.0 coloring page SVGs have ~10-15 elements each. A 30-50x increase in DOM node count causes visible jank on touch interactions and slow initial rendering on iPad Safari.

**Why it happens:** vtracer is designed for faithful raster-to-vector conversion, not for producing interactive-friendly SVGs. Its "stacked" mode avoids holes by layering shapes, but each layer is a separate DOM node. AI-generated kawaii images have far more visual detail than hand-drawn line art.

**Consequences:**
- Laggy touch response on coloring pages
- Large SVG files (100KB+ per page vs current 2-3KB hand-crafted SVGs)
- Rendering SVG to canvas for flood fill takes longer with more paths
- Memory pressure on iPad Safari

**Prevention:**
- **For coloring pages:** Use vtracer in `binary` mode (the `simplify=True` path already in `trace.py`) to produce clean black-and-white outlines only. The user adds the color -- you only need line art.
- **For dress-up:** Keep path count manageable. Run SVGO optimization post-trace. Use aggressive `filter_speckle` (20+) and low `color_precision` (3-4) to reduce path count.
- **Set a complexity budget:** target <50 paths per coloring page outline, <100 paths per dress-up component SVG.
- **Test on actual iPad hardware** early and often. Simulator performance does not match real device performance.

**Impact on existing code:**
- `trace.py` already has the `simplify` parameter -- use it for coloring pages
- For dress-up SVGs, add an SVGO post-processing step to the pipeline

**Detection:** If `document.querySelectorAll("svg path").length` exceeds 100 on any single view, investigate performance on a real iPad.

**Confidence:** HIGH -- SVG DOM performance degradation with path count is well-documented. The project's own `trace.py` already has the `simplify` parameter for this reason.

---

### Pitfall 3: Canvas Memory Limit on iPad Safari Crashes the App Silently

**What goes wrong:** iPad Safari has a hard canvas memory limit of ~384MB (varies by device and iOS version). Each canvas pixel uses 4 bytes (RGBA). A single 1024x1024 canvas uses ~4MB. Creating multiple canvases (one per coloring page, or temp canvases for flood fill processing) without releasing them causes Safari to either silently invalidate canvases or crash the tab entirely. Calling `getImageData()` on an invalidated canvas throws `InvalidStateError`.

**Why it happens:** Safari hoards canvas memory even for canvases no longer referenced in JavaScript. Navigating between coloring pages (back to gallery, open a new page) accumulates unreleased canvases. The v1.0 app has zero canvas elements, so this is an entirely new concern.

**Consequences:** The app crashes or shows a blank canvas after the user opens several coloring pages in sequence. The child thinks the app is broken. Safari may kill the tab entirely with no recovery.

**Prevention:**
- **Always release canvases** when navigating away from a coloring page:
  ```javascript
  function releaseCanvas(canvas) {
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext('2d');
    ctx && ctx.clearRect(0, 0, 1, 1);
  }
  ```
- Use a **single shared canvas element**, reused across coloring pages (do not create a new canvas per page)
- Keep canvas dimensions matching the SVG viewBox (600x800 for current pages) -- do NOT double for retina resolution on the flood fill buffer
- Call `releaseCanvas()` in the router when navigating away from the coloring view

**Impact on existing code:**
- The hash router in `app.js` needs a cleanup hook -- when leaving the coloring view, release the canvas
- Consider adding cleanup to `resetColoringState()` in `coloring.js`

**Detection:** Test by opening and closing 10+ coloring pages in sequence on a real iPad. Watch for "Total canvas memory use exceeds the maximum limit" warnings in Safari Web Inspector.

**Confidence:** HIGH -- Apple Developer Forums and multiple libraries document this exact issue.

---

### Pitfall 4: AI-Generated Art Inconsistency Makes Dress-Up Parts Look Mismatched

**What goes wrong:** Generating tail-1, tail-2, tail-3 as separate API calls produces tails that vary in size, angle, line weight, color palette, and style. When combined in the dress-up interface, the parts look like they were drawn by different artists. A child will notice this immediately.

**Why it happens:** Generative models are stochastic. Even with identical style descriptions, each generation has variance. OpenAI's own documentation acknowledges the model "may occasionally struggle to maintain visual consistency for recurring characters or brand elements across multiple generations."

**Consequences:** The dress-up feature looks like a collage. Parts that do not align at seam points (tail-to-body, hair-to-head) create obvious visual gaps or overlaps. This breaks the illusion and the delight.

**Prevention:**
- **Generate the full character first**, then create variants using the **edit API with masks** -- do NOT generate parts independently
- Use a single reference image as the base character; edit only the region you want to vary (e.g., mask the tail area, regenerate with "different tail style")
- Establish alignment anchors: define exact pixel coordinates where parts connect and enforce them
- Generate all variants in a single session/conversation where the model can reference prior context
- Consider GPT Image 1.5 (stronger at edit consistency than GPT Image 1)
- **Pre-generate all assets offline** during the build pipeline -- never generate at runtime
- Have a human QA step: review all variants side-by-side before shipping

**Impact on existing code:**
- The `PARTS` definition in `dressup.js` expects `tail-1`, `tail-2`, etc. as `<defs>` in the SVG. The pipeline must produce parts that fit this system.
- The `<defs>` + `<use>` pattern from v1.0 is the right architecture -- the challenge is producing the assets, not the code.

**Detection:** Place all tail variants side-by-side in a test page. If a non-technical person notices style differences, the variants need regeneration.

**Confidence:** HIGH -- OpenAI docs + community reports confirm this is a persistent issue.

---

### Pitfall 5: GitHub Pages Base Path Breaks All `fetch()` Calls

**What goes wrong:** The current code uses root-relative paths like `fetch("/assets/svg/mermaid.svg")` (line 52 of `app.js`). On GitHub Pages project sites, the app is served from `https://username.github.io/mermaids/`, not the root. A fetch to `/assets/svg/mermaid.svg` resolves to `https://username.github.io/assets/svg/mermaid.svg` (missing the `/mermaids/` prefix), returning 404. Every fetch-based asset load breaks.

**Why it happens:** FastAPI serves from root (`/`), so root-relative paths work in development. GitHub Pages project sites serve from a subdirectory. This is the single most common GitHub Pages deployment issue.

**Consequences:** The app shows "Could not load mermaid" and "Could not load coloring page" errors for every view. Total breakage, zero functionality.

**Prevention:**
- **Audit every `fetch()` call and asset path.** Replace root-relative paths (`/assets/...`) with relative paths (`assets/...`)
- Specific fix needed: `app.js` line 52 -- change `fetch("/assets/svg/mermaid.svg")` to `fetch("assets/svg/mermaid.svg")`
- The `COLORING_PAGES` file paths in `coloring.js` (lines 28-31) already use relative paths (`assets/svg/coloring/...`) -- these are correct and will work
- The hash-based routing (`#/home`, `#/dressup`, `#/coloring`) is already GitHub Pages-compatible -- the hash is never sent to the server, so no 404 issues for navigation
- Optionally add a `<base href>` tag to `index.html`, but relative paths are simpler and less error-prone
- **Test on GitHub Pages immediately after first deployment**, before building new features

**Impact on existing code:**
- `app.js`: one `fetch()` call needs path fix
- `coloring.js`: paths are already relative (no change needed)
- Any new asset loading code must use relative paths

**Detection:** Open browser Network tab on the deployed site. Any 404s on asset loads indicate broken paths.

**Confidence:** HIGH -- documented by GitHub, freeCodeCamp, Smashing Magazine, and many developers.

---

## Moderate Pitfalls

---

### Pitfall 6: Anti-Aliasing Fringe on Flood Fill Edges

**What goes wrong:** When the browser renders SVG line art onto a canvas, it anti-aliases the edges of strokes, creating semi-transparent pixels at stroke boundaries. A naive flood fill with tolerance=0 stops at these anti-aliased pixels, leaving an unfilled fringe between the fill color and the line. Setting tolerance too high bleeds the fill through lines into adjacent regions.

**Prevention:**
- Use a tolerance of ~30-50 for flood fill color matching (not 0 which stops at anti-aliased pixels, not 128 which bleeds through lines)
- Consider a `toleranceFade` approach that applies graduated alpha at edge pixels
- Ensure traced line art has a stroke width of at least 2-3px -- thicker lines reduce fringe problems compared to 1px lines
- If using vtracer binary mode, verify the output stroke width is adequate

**Detection:** Flood fill a region and zoom in to the edge where fill meets outline. If there is a visible white/unfilled gap between the color and the line, tolerance is too low. If color leaks through to adjacent regions, tolerance is too high.

**Confidence:** HIGH -- the most common complaint in canvas flood fill implementations.

---

### Pitfall 7: Transparent Background Generation Cuts Holes in White Character Parts

**What goes wrong:** OpenAI's image API with `background: "transparent"` frequently makes white or light-colored parts of the character (eyes, belly, light-colored skin) transparent instead of white. Community reports indicate this happens in ~80% of generations when the character has large white areas.

**Prevention:**
- Generate on a **solid non-character color background** (bright green, magenta, or another color that does not appear in the character)
- Use a programmatic background removal tool (`rembg` Python library or similar) as a post-processing step instead of relying on the API's `transparent` parameter
- For dress-up parts that need transparency for layering, remove the background programmatically after generation
- Validate each generated image before processing: check that character body pixels are opaque

**Impact on existing code:**
- Add a background removal step to the art pipeline (`trace.py` or a new pipeline module)

**Confidence:** MEDIUM -- based on multiple OpenAI Developer Forum threads from 2025. OpenAI may improve this in future model updates.

---

### Pitfall 8: Dress-Up Part Decomposition from a Single Image Is Unreliable

**What goes wrong:** The plan calls for decomposing AI art into swappable dress-up parts. Taking a single generated mermaid image and automatically splitting it into head, hair, body, tail, and accessories requires semantic segmentation at a level that current tools handle inconsistently. AI layer decomposition tools (like Qwen-Image-Layered, released Dec 2025) split by depth and semantics but not by the specific part boundaries a dress-up game needs (hair-to-head boundary, waist-to-tail boundary at exact pixel coordinates).

**Prevention:**
- **Do not attempt fully automatic decomposition.** Instead:
  1. Generate the full mermaid character as a reference
  2. Use the OpenAI edit API with explicit masks to generate variants of specific regions
  3. Or: generate full character variants and manually crop/mask parts in the pipeline script
- Define part boundaries as fixed pixel coordinates in the pipeline configuration
- Accept that this step requires some manual curation, at least for the first asset set
- The v1.0 `<defs>` + `<use>` SVG pattern for part swapping is architecturally sound -- the challenge is producing the assets, not the rendering code

**Confidence:** MEDIUM -- AI layer decomposition is rapidly evolving but not yet reliable for precise game-ready part boundaries.

---

### Pitfall 9: Migrating to Static Deployment Breaks the 37 Playwright Tests

**What goes wrong:** All 37 Playwright E2E tests run against the FastAPI server. Removing FastAPI or changing the serving setup breaks every test. If you keep FastAPI only for tests but deploy differently, the two environments can diverge and bugs slip through.

**Prevention:**
- **Keep FastAPI as the local development and test server.** It is 16 lines of code (`app.py`) and costs nothing.
- The deployment pipeline copies `frontend/` to GitHub Pages. The test suite runs against FastAPI serving the same `frontend/` directory. Both serve the same files.
- Do NOT introduce a separate test server, test configuration, or test-only paths
- Add one CI verification step: serve the `frontend/` directory with `python -m http.server` (no FastAPI) and run a smoke test to confirm the app loads. This catches any accidental dependency on FastAPI.

**Impact on existing code:**
- `app.py` stays as-is (it is just `StaticFiles(directory=_frontend_dir, html=True)`)
- GitHub Actions workflow deploys `frontend/` to Pages
- Playwright tests continue to use `uvicorn` as before

**Detection:** If any Playwright test fails with connection errors after deployment changes, the test infrastructure is broken.

**Confidence:** HIGH -- preserving the existing test infrastructure is straightforward.

---

### Pitfall 10: Touch Event Handling Must Change for Canvas Coloring Surface

**What goes wrong:** The v1.0 touch system uses `pointerdown` on SVG elements with `event.target.closest("[data-region]")` for region detection (see `app.js` line 209 and `touch.js`). Canvas elements have no child elements -- `closest()` and all DOM traversal methods return nothing useful when the tap target is a `<canvas>`. The touch handler for flood fill must calculate tap position in canvas pixel coordinates and pass those directly to the flood fill algorithm.

**Prevention:**
- Write a **new touch handler** for the canvas coloring surface that:
  1. Gets pointer coordinates from the event
  2. Converts to canvas pixel coordinates using `getBoundingClientRect()` and accounting for CSS scaling
  3. Passes (x, y) to the flood fill function operating on `ImageData`
- The sparkle effect system (`sparkle.js`) already has `getSVGPoint()` for SVG coordinate conversion -- a similar but canvas-specific approach is needed
- **Keep the SVG-based touch handling for dress-up** (it still uses SVG DOM with `<defs>` and `<use>`)
- Do not try to make a single unified handler for both SVG and canvas views

**Impact on existing code:**
- The pointerdown delegation in `app.js` `openColoringPage()` (lines 205-213) needs to be replaced with canvas-aware touch handling
- `touch.js` `initTouch()` remains unchanged for the dress-up view
- `sparkle.js` effects may need adaptation if sparkles should appear on the canvas surface

**Confidence:** HIGH -- direct consequence of switching from SVG DOM to canvas rendering.

---

### Pitfall 11: SVG-to-Canvas Rendering Inconsistency in Safari

**What goes wrong:** Rendering SVG to canvas (via `drawImage()` with an `<img>` whose src is a data URI or blob URL of SVG content) produces slightly different results in Safari vs Chrome. Safari handles certain SVG features (foreign objects, CSS-driven styling, text elements) differently. If the flood fill depends on exact pixel color matching, cross-browser rendering differences cause fill behavior to vary.

**Prevention:**
- Use only basic SVG features: `<path>`, `<circle>`, `<rect>` with solid fills and strokes. No `foreignObject`, no CSS within SVG, no `<text>`.
- When rendering SVG to canvas, use the `Image()` + `data:` URI approach or a library like `canvg`, not `URL.createObjectURL()` (which has CORS complications in some Safari versions)
- Set `ctx.imageSmoothingEnabled = false` when rendering line art to minimize anti-aliasing variance
- Test flood fill behavior on Safari specifically since that is the target platform

**Confidence:** MEDIUM -- SVG rendering differences are well-known but impact depends on SVG complexity. Simple binary-mode line art should be low-risk.

---

## Minor Pitfalls

---

### Pitfall 12: OpenAI API Costs Compound During Prompt Iteration

**What goes wrong:** The art generation pipeline makes multiple API calls per asset set (full character + variants + coloring pages). Each generation costs $0.04-0.08+. Iterating on prompts 10+ times to get the style right costs $10-20+, which adds up for a hobby project.

**Prevention:**
- Cache every generation locally with its prompt hash
- Use `gpt-image-1-mini` for iteration and style experimentation, `gpt-image-1` or `gpt-image-1.5` only for final assets
- Set a budget cap in the pipeline script (warn after N generations)
- Run the pipeline in batch mode with explicit human review before regenerating

**Confidence:** HIGH -- straightforward cost management.

---

### Pitfall 13: Do Not "Upgrade" Hash Routing -- It Is Already Correct

**What goes wrong:** Developers sometimes "upgrade" from hash routing (`#/dressup`) to History API routing (`/dressup`) during a refactor. History API routing breaks on GitHub Pages because the server returns 404 for any path other than `/index.html`. There is no server-side redirect capability on GitHub Pages.

**Prevention:**
- **Do not change the routing strategy.** The current hash-based router in `app.js` (lines 220-243) is already GitHub Pages-compatible. This is a solved problem.
- The 404.html workaround for History API routing exists but adds complexity for no benefit in this app.

**Confidence:** HIGH -- the current routing is correct for the target deployment.

---

### Pitfall 14: Retina Display Makes Canvas Look Blurry But Doubling Resolution Costs Memory

**What goes wrong:** iPad displays are 2x retina. A canvas element sized 600x800 in CSS occupies 1200x1600 physical pixels. If the canvas buffer is 600x800, content looks blurry. But setting the buffer to 1200x1600 quadruples memory usage and makes flood fill 4x slower (4x more pixels to scan).

**Prevention:**
- For the flood fill data buffer: use CSS dimensions (600x800), NOT retina resolution. Speed matters more than sub-pixel accuracy for a fill operation.
- For the display layer: use the SVG line art as a crisp overlay on top of the canvas. SVGs render at full retina resolution automatically. The canvas only holds the fill colors.
- Architecture: **SVG overlay (lines, crisp) on top + canvas underlay (fills, can be lower-res)**
- This gives the best of both worlds: crisp outlines at retina resolution, fast flood fills at 1x resolution.

**Confidence:** MEDIUM -- the visual impact depends on the app's layout, but the layered approach is well-established.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Art generation pipeline | Pitfall 4 (inconsistency), 7 (transparency holes), 12 (costs) | Generate full character first, use edit API with masks; solid background + programmatic removal; cache everything |
| SVG tracing with vtracer | Pitfall 2 (too many paths) | Binary mode for coloring outlines; aggressive simplification; SVGO post-processing |
| Flood fill coloring | Pitfall 1 (requires canvas), 3 (canvas memory), 6 (anti-aliasing fringe), 10 (touch events), 14 (retina) | Canvas layer under SVG overlay; release canvases on nav; tolerance ~30-50; new touch handler; 1x resolution fill buffer |
| Dress-up with AI art | Pitfall 4 (inconsistency), 8 (decomposition) | Edit API with masks over base image; fixed part boundaries; manual curation |
| GitHub Pages deployment | Pitfall 5 (base path breaks fetch), 9 (test suite), 13 (keep hash routing) | Fix `/assets/` to `assets/`; keep FastAPI for tests; do not change router |
| iPad Safari compatibility | Pitfall 2 (DOM perf), 3 (canvas memory), 11 (SVG rendering), 14 (retina) | Path count budgets; canvas lifecycle management; test on real hardware |

---

## Key Architectural Insight: Hybrid SVG+Canvas for Coloring

The single most important architectural decision for v1.1 is using a **hybrid SVG+Canvas approach** for coloring pages:

1. **SVG layer** (top): line art rendered at full retina resolution, always crisp, provides the visual outlines
2. **Canvas layer** (bottom): flood fill target at 1x resolution, handles user interaction and color data

This simultaneously addresses:
- **Pitfall 1** (flood fill needs canvas): canvas provides the pixel data
- **Pitfall 2** (too many SVG paths): only line art SVG in the DOM, not full-color traced SVG
- **Pitfall 3** (canvas memory): single shared canvas, managed lifecycle
- **Pitfall 6** (anti-aliasing): SVG overlay hides any fringe at fill edges
- **Pitfall 14** (retina): SVG provides retina-quality lines; canvas can be lower-res

The dress-up feature should remain SVG-only (the `<defs>` + `<use>` pattern from v1.0 is correct and performant).

---

## Sources

- [Canvas memory limit on iOS Safari (PQINA)](https://pqina.nl/blog/total-canvas-memory-use-exceeds-the-maximum-limit)
- [Canvas area limits in Safari (PQINA)](https://pqina.nl/blog/canvas-area-exceeds-the-maximum-limit/)
- [Apple Developer Forum: canvas memory](https://developer.apple.com/forums/thread/687866)
- [Konva canvas limits in Safari iOS (2024)](https://longviewcoder.com/2024/02/09/konva-canvas-limits-in-safari-ios-explainer/)
- [q-floodfill: optimized non-recursive flood fill](https://github.com/pavelkukov/q-floodfill)
- [FloodFill2D: tolerance, alpha, and anti-aliasing handling](https://github.com/blindman67/FloodFill2D)
- [Instant colour fill with HTML Canvas (preprocessed approach)](https://shaneosullivan.wordpress.com/2023/05/23/instant-colour-fill-with-html-canvas/)
- [Canvas flood fill that doesn't kill the browser](https://ben.akrin.com/an-html5-canvas-flood-fill-that-doesnt-kill-the-browser/)
- [GitHub Pages SPA routing limitations](https://github.com/orgs/community/discussions/64096)
- [spa-github-pages: 404.html workaround](https://github.com/rafgraph/spa-github-pages)
- [Fixing broken relative links on GitHub Pages](https://maximorlov.com/deploying-to-github-pages-dont-forget-to-fix-your-links/)
- [GitHub Pages publishing source docs](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [OpenAI Image Generation API guide](https://platform.openai.com/docs/guides/image-generation)
- [OpenAI GPT Image 1.5 model docs](https://platform.openai.com/docs/models/gpt-image-1.5)
- [OpenAI: transparent background cuts holes in white areas](https://community.openai.com/t/gpt-image-1-transparency-remove-background-also-cuts-out-other-white-spots-of-the-image/1273481)
- [OpenAI: character consistency across generations](https://community.openai.com/t/need-for-character-consistency-and-style-locking-in-image-generation/1232362)
- [Character consistency guide for ChatGPT image generation](https://blog.laozhang.ai/ai-tools/mastering-character-consistency-chatgpt-image-generator/)
- [vtracer: parameters and modes](https://github.com/visioncortex/vtracer)
- [vtracer core functionality (DeepWiki)](https://deepwiki.com/visioncortex/vtracer/7-core-functionality)
- [Improving SVG rendering performance](https://codepen.io/tigt/post/improving-svg-rendering-performance)
- [High Performance SVGs (CSS-Tricks)](https://css-tricks.com/high-performance-svgs/)
- [Qwen-Image-Layered: AI layer decomposition (Dec 2025)](https://dev.to/czmilo/2025-complete-guide-qwen-image-layered-revolutionary-ai-image-layer-decomposition-technology-4mm7)
- [Raster to vector conversion gap issues](https://community.adobe.com/t5/illustrator-discussions/raster-to-vector-conversion-leaves-gaps-in-paths/td-p/9932299)
- [OpenAI complete workflow guide for gpt-image-1](https://img.ly/blog/openai-gpt-4o-image-generation-api-gpt-image-1-a-complete-guide-for-creative-workflows-for-2025/)
