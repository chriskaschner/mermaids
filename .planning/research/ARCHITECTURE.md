# Architecture Patterns: v1.1 Art & Deploy Integration

**Domain:** Kids creative activity web app -- integrating AI art pipeline, flood-fill coloring, and static deployment into existing v1.0 architecture
**Researched:** 2026-03-09
**Confidence:** HIGH (based on direct codebase analysis + verified research)

## Existing Architecture (What We Have)

The v1.0 architecture is a client-heavy static web app served by FastAPI:

```
+------------------------------------------------------------+
|                   iPad Safari Browser                       |
|                                                             |
|  index.html (#app container + #nav-bar)                     |
|                                                             |
|  app.js (hash router: #/home, #/dressup, #/coloring)       |
|    |                                                        |
|    +-- renderDressUp() --> fetches mermaid.svg              |
|    |     dressup.js: SVG <defs>+<use> variant system        |
|    |     touch.js: pointer event delegation on [data-region] |
|    |     sparkle.js: SVG particle effects                   |
|    |                                                        |
|    +-- renderColoring() --> gallery of 4 SVG pages          |
|          coloring.js: tap [data-region] to fill             |
|                                                             |
+----------------------------+--------------------------------+
                             |
                       HTTP (static)
                             |
+----------------------------v--------------------------------+
|              FastAPI (app.py)                                |
|  Mounts frontend/ as StaticFiles at /                       |
+-------------------------------------------------------------+

Pipeline (offline, not runtime):
  src/mermaids/pipeline/trace.py
  vtracer: raster PNG/JPG --> SVG
```

### Key Architectural Patterns Already Established

1. **SVG `<defs>` + `<use>` for dress-up variants.** Variant shapes live inside `<defs>`. Three `<use>` elements (`#active-tail`, `#active-hair`, `#active-acc`) reference variants by `href`. Swapping a part = `useEl.setAttribute("href", "#tail-2")`.

2. **`data-region` attribute for interactive SVG areas.** Both coloring and dress-up use `[data-region]` groups as tap targets. Coloring fills via `fillRegion()` which sets `fill` on child paths. Dress-up uses `swapPart()` and `recolorActivePart()`.

3. **Module pattern with separate state lifecycles.** Each activity module (dressup.js, coloring.js) owns its own state object, undo stack, and reset function. They share a COLORS array by coincidence, not by import.

4. **Hash-based routing without build step.** app.js listens to `hashchange`, dispatches to view renderers. No bundler, no transpilation, vanilla ES modules.

5. **FastAPI as pure static file server.** app.py contains zero business logic -- just `StaticFiles(directory=frontend_dir, html=True)`.

## Target Architecture (What We Need)

```
+------------------------------------------------------------+
|                   iPad Safari Browser                       |
|                                                             |
|  index.html (same shell, same nav)                         |
|                                                             |
|  app.js (same router, same 3 routes)                       |
|    |                                                        |
|    +-- renderDressUp()                                      |
|    |     NEW: fetches kawaii mermaid SVG (AI-generated)      |
|    |     dressup.js: SAME <defs>+<use> pattern              |
|    |     NEW: PARTS map updated for new variant IDs         |
|    |     sparkle.js: unchanged                              |
|    |                                                        |
|    +-- renderColoring()                                     |
|    |     NEW: gallery shows AI-generated coloring pages     |
|    |     openColoringPage()                                 |
|    |       CHANGED: canvas-based flood fill replaces        |
|    |                 SVG region-based tap-to-fill           |
|    |       NEW: SVG rendered to canvas, flood fill on       |
|    |            canvas pixels, line art SVG overlaid on top |
|    |                                                        |
+----------------------------+--------------------------------+
                             |
                    HTTP (static files)
                             |
+----------------------------v--------------------------------+
|  GitHub Pages (replaces FastAPI for production)             |
|  Serves frontend/ directory as-is                          |
+-------------------------------------------------------------+

Pipeline (offline, dev-time only, NOT in production):
  src/mermaids/pipeline/generate.py   <-- NEW: OpenAI API
  src/mermaids/pipeline/trace.py      <-- MODIFIED: coloring-page mode
  src/mermaids/pipeline/assemble.py   <-- NEW: SVG post-processing
```

## Component Change Analysis

### Components That Stay Unchanged

| Component | File | Why No Change |
|-----------|------|---------------|
| App shell / HTML | `frontend/index.html` | Same layout, same nav bar, same `#app` container |
| Hash router | `frontend/js/app.js` (routing logic) | Same 3 routes, hash routing works on GitHub Pages |
| Sparkle effects | `frontend/js/sparkle.js` | Purely decorative, art-agnostic |
| Touch delegation | `frontend/js/touch.js` | Still delegates to `[data-region]` elements |
| CSS layout | `frontend/css/style.css` | Same iPad-optimized layout applies to new art |

### Components That Need Modification

| Component | File | What Changes | Why |
|-----------|------|-------------|-----|
| Dress-up state | `frontend/js/dressup.js` | PARTS map IDs, variant preview SVGs, possibly category names | AI-generated mermaid will have different part IDs and different variant counts |
| Coloring interaction | `frontend/js/coloring.js` | Replace `fillRegion()` with canvas flood-fill | AI-generated art has arbitrary shapes, not pre-tagged `data-region` groups |
| Coloring page rendering | `frontend/js/app.js` (`openColoringPage`) | Canvas overlay architecture instead of pure SVG tap | Flood fill requires pixel-level operations on a canvas |
| COLORING_PAGES metadata | `frontend/js/coloring.js` | New page entries for AI-generated pages | New art assets |
| vtracer pipeline | `src/mermaids/pipeline/trace.py` | Add coloring-page-optimized settings | AI-generated images need different trace params than the current binary/color modes |

### New Components to Build

| Component | File | Responsibility |
|-----------|------|----------------|
| **Art generation script** | `src/mermaids/pipeline/generate.py` | Call OpenAI gpt-image-1 API with kawaii mermaid prompts, save PNGs to `assets/generated/` |
| **SVG assembly script** | `src/mermaids/pipeline/assemble.py` | Post-process vtracer SVG output: add `data-region` attributes, create `<defs>` structure for dress-up variants, inject hit-area rects |
| **Flood-fill module** | `frontend/js/floodfill.js` | Canvas-based flood fill algorithm (iterative span fill), pixel color comparison with tolerance |
| **GitHub Actions workflow** | `.github/workflows/deploy.yml` | Deploy `frontend/` directory to GitHub Pages on push to main |

## Detailed Integration Design

### 1. AI Art Pipeline (Offline, Dev-Time)

The art pipeline runs on the developer's machine, not at runtime. It produces static SVG files that get committed to the repo.

```
Developer runs pipeline:

  generate.py                     trace.py                    assemble.py
  +-----------+                  +-----------+                +-----------+
  | OpenAI    |  kawaii PNG      | vtracer   |  raw SVG      | Post-     |  final SVG
  | gpt-image |  ------------->  | raster-to |  ---------->  | process   |  ---------->  frontend/assets/
  | -1 API    |  1024x1024       | -SVG      |  paths only   | for app   |  with defs,
  +-----------+                  +-----------+                +-----------+  regions, etc.
       |                              |                            |
       |  Prompt includes:            |  Settings differ for:     |  For dress-up:
       |  - "kawaii style"            |  - dress-up (color mode,  |  - Split into parts
       |  - specific part desc        |    preserve fills)        |  - Wrap in <defs> <g id="">
       |  - white background          |  - coloring (binary mode, |  - Add <use> references
       |  - consistent character      |    clean outlines)        |
       |                              |                           |  For coloring:
       |                              |                           |  - Keep as-is (outlines)
       |                              |                           |  - Ensure clean strokes
```

**OpenAI API usage (gpt-image-1):**

```python
from openai import OpenAI

client = OpenAI()

result = client.images.generate(
    model="gpt-image-1",
    prompt="kawaii chibi mermaid, simple flat colors, white background, ...",
    size="1024x1024",
    quality="high",
    output_format="png",
)
```

Use gpt-image-1 (not DALL-E 3, which is deprecated May 2026). gpt-image-1.5 is also available with faster generation but same API surface. Key parameters: `quality="high"` for clean lines suitable for tracing, `size="1024x1024"` matching the vtracer input pipeline.

**Consistency strategy:** Use a detailed style guide prompt prefix appended to all requests. Include specific color palette hex values, art style descriptors ("kawaii chibi", "thick black outlines", "flat colors"), and character description. Generate multiple candidates and manually curate.

### 2. Dress-Up SVG: Adapting AI Art to defs+use

This is the hardest integration point. The current system works because the mermaid SVG was hand-crafted with `<defs>` containing `<g id="tail-1">`, `<g id="tail-2">`, etc., and `<use id="active-tail" href="#tail-1">` references them.

**The problem:** AI-generated art comes out as a single raster image. After vtracer conversion, it becomes a flat SVG with stacked paths -- no semantic grouping, no part boundaries, no IDs.

**The solution: Semi-automated assembly with manual curation.**

The pipeline generates one image per variant (not one image with all variants):

```
Prompt: "kawaii mermaid tail, flowing style, teal, isolated on white background"
  --> tail-1.png --> vtracer --> tail-1-raw.svg

Prompt: "kawaii mermaid tail, forked style, teal, isolated on white background"
  --> tail-2.png --> vtracer --> tail-2-raw.svg
```

Then `assemble.py` wraps each raw SVG into the `<defs>` structure:

```python
def assemble_dressup_svg(variant_svgs: dict, template_path: Path) -> str:
    """
    variant_svgs: {"tail-1": "tail-1-raw.svg", "tail-2": "tail-2-raw.svg", ...}
    template_path: base SVG with body, face, <use> elements

    Produces final mermaid.svg with:
    - <defs> containing all variants as <g id="tail-1">, etc.
    - <use> elements referencing the defaults
    - Body/face elements (non-swappable) inline
    """
```

**Key constraint:** Each variant SVG must align spatially. The prompts must specify consistent positioning ("centered, facing forward, occupying the lower half of the frame"). Post-processing may need to normalize viewBox coordinates and translate paths to align with the body.

**What changes in dressup.js:**

```javascript
// PARTS map updates to match new variant IDs from AI-generated art
export const PARTS = {
  tail: ["tail-1", "tail-2", "tail-3"],    // same structure, new art
  hair: ["hair-1", "hair-2", "hair-3"],    // same structure, new art
  acc: ["acc-none", "acc-1", "acc-2"],      // same structure, new art
};

// getVariantPreviewSVG() needs new preview thumbnails
// Could auto-generate from the variant SVGs or use separate small PNGs
```

The defs+use swap mechanism itself does not change. `swapPart()`, `recolorActivePart()`, and the undo stack all work identically with new art as long as the SVG structure follows the same convention: variants in `<defs>` with matching IDs, `<use>` elements with `href` attributes.

**Recoloring consideration:** The current `recolorActivePart()` sets ALL fill-bearing child elements to a single color. This works with simple hand-drawn shapes. AI-traced SVGs may have many more paths with varied colors. Two options:

1. **Keep the all-one-color approach.** Simple, works for kawaii style where each part is basically one hue. The user picks "pink" and the whole tail turns pink.
2. **Hue-shift instead of fill replacement.** Apply an SVG filter (`feColorMatrix`) to shift the hue while preserving value/saturation variation. More visually sophisticated but adds complexity.

Recommendation: **Keep the all-one-color approach.** It matches the existing code, the 6-year-old audience prefers bold simple colors, and kawaii art style is inherently flat-color. If the traced SVG has too many paths with slight color variations, the assemble step should merge or simplify them.

### 3. Coloring Pages: Canvas Flood-Fill Architecture

This is the biggest architectural change. The current coloring uses SVG `data-region` groups -- hand-tagged semantic areas that you tap to fill. AI-generated coloring pages cannot have pre-tagged regions because the art is arbitrary.

**Two-layer canvas+SVG architecture:**

```
+-----------------------------------------------+
|  .coloring-page-container                     |
|                                                |
|  +-------------------------------------------+|
|  | <canvas id="fill-canvas">                 || <-- bottom layer: flood-fill target
|  | (hidden behind SVG, same dimensions)       ||     user taps here for fill
|  +-------------------------------------------+|
|  +-------------------------------------------+|
|  | <svg> (line art overlay)                   || <-- top layer: black outlines
|  | pointer-events: none                       ||     visually on top, clicks pass through
|  +-------------------------------------------+|
|                                                |
+-----------------------------------------------+
```

**How it works:**

1. Load the coloring page SVG (black outlines on white background)
2. Render the SVG onto a `<canvas>` element (using Image + drawImage)
3. Display the SVG on top of the canvas with `pointer-events: none`
4. User taps --> hit lands on the canvas
5. Run flood-fill algorithm at the tap pixel coordinates on the canvas imageData
6. The canvas shows the filled color; the SVG lines remain crisp on top

**Why this approach:**

- **Works with ANY image.** No manual region tagging needed. AI-generated art works directly.
- **Flood fill is intuitive.** Every coloring app uses it. The 6-year-old already understands "tap inside the lines."
- **Lines stay crisp.** SVG outlines render at device resolution, unaffected by canvas pixel manipulation below.
- **Undo is straightforward.** Save the canvas imageData before each fill, restore on undo.

**Flood-fill algorithm choice: Iterative span fill.**

The recursive approach causes stack overflow on large regions. The iterative span fill algorithm is the standard choice -- it processes horizontal spans, which is cache-friendly and fast. On a 1024x1024 canvas (the max relevant size for this app), it completes in under 50ms on iPad hardware.

```javascript
// frontend/js/floodfill.js
export function floodFill(ctx, startX, startY, fillColor, tolerance = 30) {
  const imageData = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
  const data = imageData.data;
  const width = ctx.canvas.width;
  const height = ctx.canvas.height;

  const startIdx = (startY * width + startX) * 4;
  const startR = data[startIdx], startG = data[startIdx+1],
        startB = data[startIdx+2], startA = data[startIdx+3];

  // Don't fill if clicking on a line (dark pixel)
  if (startR + startG + startB < 100) return;

  // Don't fill if already the target color
  const [fillR, fillG, fillB] = hexToRgb(fillColor);
  if (Math.abs(startR-fillR) + Math.abs(startG-fillG) + Math.abs(startB-fillB) < 10) return;

  // Iterative span fill
  const stack = [[startX, startY]];
  const visited = new Uint8Array(width * height);

  while (stack.length > 0) {
    let [x, y] = stack.pop();
    // Scan left to find span start
    while (x > 0 && matchesTarget(data, (y*width+x-1)*4, startR, startG, startB, startA, tolerance)) x--;
    let spanAbove = false, spanBelow = false;
    // Scan right, filling pixels
    while (x < width && matchesTarget(data, (y*width+x)*4, startR, startG, startB, startA, tolerance)) {
      const idx = (y * width + x) * 4;
      data[idx] = fillR; data[idx+1] = fillG; data[idx+2] = fillB; data[idx+3] = 255;
      visited[y * width + x] = 1;
      // Check row above
      if (y > 0) { /* push spans */ }
      // Check row below
      if (y < height-1) { /* push spans */ }
      x++;
    }
  }
  ctx.putImageData(imageData, 0, 0);
}
```

**Color tolerance is critical.** vtracer-generated outlines are anti-aliased. Without tolerance (say 20-40 in RGB distance), the flood fill will leak through anti-aliased edges. With tolerance, it fills smoothly up to the line boundaries.

**What changes in coloring.js:**

The `fillRegion()` function is replaced entirely. The module shifts from SVG DOM manipulation to canvas pixel manipulation:

```javascript
// OLD (v1.0): SVG region-based
export function fillRegion(regionGroup, color) {
  getFillableElements(regionGroup).forEach(el => el.setAttribute("fill", color));
}

// NEW (v1.1): Canvas flood-fill
import { floodFill } from "./floodfill.js";

export function fillAtPoint(ctx, x, y, color) {
  // Save imageData for undo before filling
  const beforeData = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
  pushUndo(() => ctx.putImageData(beforeData, 0, 0));

  floodFill(ctx, Math.round(x), Math.round(y), color);
}
```

**What changes in app.js (`openColoringPage`):**

```javascript
// Instead of wiring pointerdown on SVG regions:
// 1. Create canvas element sized to match SVG viewBox
// 2. Render SVG to canvas via Image
// 3. Overlay SVG on top with pointer-events: none
// 4. Wire pointerdown on canvas for flood fill
```

### 4. GitHub Pages Deployment

This is the simplest integration. The app already uses hash routing (`#/home`, `#/dressup`, `#/coloring`), which works perfectly with GitHub Pages -- no 404.html hack needed because the browser never requests a server path other than `/`.

**What needs to happen:**

1. **Remove FastAPI dependency for production.** The app.py file becomes dev-only (for local testing with `uvicorn`). Production is pure static files.

2. **Asset paths must be relative.** Currently, `renderDressUp()` fetches `/assets/svg/mermaid.svg` (absolute path). On GitHub Pages with a project site (e.g., `username.github.io/mermaids/`), the base path is `/mermaids/`, so absolute paths break. Fix: use relative paths (`assets/svg/mermaid.svg`) or a `<base>` tag.

3. **GitHub Actions workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: frontend
      - id: deployment
        uses: actions/deploy-pages@v4
```

4. **No build step required.** The frontend directory is deployed as-is. No bundler, no transpilation. This is a major advantage of the vanilla JS architecture.

**FastAPI stays for local development.** Run `uvicorn mermaids.app:app` during development. GitHub Pages replaces it for production.

### 5. Asset Path Fix (Critical for GitHub Pages)

The current code uses paths starting with `/` which assume the app is served from the root:

```javascript
// Current (breaks on GitHub Pages project site):
const resp = await fetch("/assets/svg/mermaid.svg");

// Fixed (works everywhere):
const resp = await fetch("assets/svg/mermaid.svg");
```

Similarly in coloring.js:
```javascript
// Current:
{ id: "page-1-ocean", file: "assets/svg/coloring/page-1-ocean.svg" }
// This one is already relative -- good. But verify ALL fetch paths.
```

And in index.html:
```html
<!-- Current (already relative -- good): -->
<link rel="stylesheet" href="css/style.css">
<script type="module" src="js/app.js"></script>
```

The only problematic path is the mermaid.svg fetch in `renderDressUp()` which uses `/assets/svg/mermaid.svg`. This must become relative.

## Data Flow: Before and After

### Dress-Up Data Flow (minimal change)

```
BEFORE (v1.0):                          AFTER (v1.1):
Hand-drawn mermaid.svg                  AI-generated mermaid.svg
  with <defs> tail-1..3,                  with <defs> tail-1..3,
  hair-1..3, acc-1..3                     hair-1..3, acc-1..3
        |                                        |
        v                                        v
  dressup.js swapPart()                   dressup.js swapPart()
  changes <use href>                      changes <use href>
  (IDENTICAL MECHANISM)                   (IDENTICAL MECHANISM)
```

### Coloring Data Flow (significant change)

```
BEFORE (v1.0):                          AFTER (v1.1):
SVG with <g data-region>                AI-generated SVG (outlines only)
        |                                        |
        v                                        v
  pointerdown on SVG                      SVG rendered to <canvas>
  event.target.closest("[data-region]")   SVG overlaid with pointer-events: none
        |                                        |
        v                                        v
  fillRegion() sets fill                  pointerdown on <canvas>
  on child elements                       get (x,y) coordinates
        |                                        |
        v                                        v
  undo: restore fill attrs               floodFill(ctx, x, y, color)
                                                  |
                                                  v
                                          undo: restore saved imageData
```

### Art Pipeline Data Flow (entirely new)

```
Developer prompt                   OpenAI API                    Local filesystem
"kawaii mermaid tail"    ------>   gpt-image-1      ------>     assets/generated/tail-1.png
                                  (1024x1024 PNG)

assets/generated/tail-1.png  --->  vtracer trace_to_svg  --->  assets/generated/tail-1-raw.svg

assets/generated/*-raw.svg   --->  assemble.py           --->  frontend/assets/svg/mermaid.svg
                                   (wraps in <defs>,            frontend/assets/svg/coloring/page-*.svg
                                    adds IDs, aligns)

Developer commits final SVGs to repo. Pipeline does NOT run in production.
```

## Component Boundaries (Updated for v1.1)

| Component | Responsibility | Communicates With | Status |
|-----------|---------------|-------------------|--------|
| **App Shell** | Navigation, layout, route dispatch | All view renderers | UNCHANGED |
| **Dress-Up Module** | Part swap, recolor, undo, completion | SVG defs+use, sparkle | MODIFIED (new PARTS IDs, new previews) |
| **Coloring Module** | Color selection, undo stack | Canvas flood-fill module | REWRITTEN (SVG regions -> canvas flood fill) |
| **Flood-Fill Module** | Pixel-level flood fill on canvas | Coloring module (caller) | NEW |
| **Touch Module** | Pointer event delegation, sparkle trigger | SVG data-region elements | UNCHANGED |
| **Sparkle Module** | Visual particle effects | SVG root element | UNCHANGED |
| **Art Gen Pipeline** | OpenAI API calls, prompt management | Filesystem (writes PNGs) | NEW (dev-only) |
| **Trace Pipeline** | Raster-to-SVG conversion | Filesystem (reads PNG, writes SVG) | MODIFIED (coloring mode params) |
| **Assembly Pipeline** | SVG post-processing, defs structure | Filesystem (reads raw SVGs, writes final SVGs) | NEW (dev-only) |
| **Deploy Workflow** | GitHub Pages deployment | GitHub Actions | NEW |

### Component Boundary Rules (Updated)

- **Pipeline code never runs in production.** It is a dev-time tool that produces static assets. The frontend has zero dependency on Python, OpenAI, or vtracer at runtime.
- **Flood-fill module is canvas-only, coloring module is the orchestrator.** `floodfill.js` is a pure function (canvas context + coordinates + color -> fills pixels). `coloring.js` manages state, undo, color selection, and wires events.
- **Dress-up SVG structure is a contract.** The pipeline MUST produce SVGs that follow the convention: `<defs>` with `<g id="tail-1">`, `<use id="active-tail" href="#tail-1">`, etc. The JS code does not care what the art looks like, only that these IDs and elements exist.

## Build Order (Dependency-Driven)

The build order is constrained by what depends on what:

```
Phase 1: Art Pipeline (no frontend dependency)
  - generate.py: OpenAI API integration
  - trace.py updates: coloring-page settings
  - assemble.py: SVG post-processing
  - Output: final SVG assets in frontend/assets/

Phase 2: Flood-Fill Coloring (depends on Phase 1 for coloring SVGs)
  - floodfill.js: canvas flood fill algorithm
  - coloring.js rewrite: canvas-based interaction
  - app.js changes: canvas+SVG overlay rendering
  - Tests: Playwright E2E for coloring

Phase 3: Dress-Up Art Swap (depends on Phase 1 for mermaid SVG)
  - dressup.js updates: new PARTS IDs, new previews
  - Verify recoloring works with traced SVG paths
  - Tests: Playwright E2E for dress-up

Phase 4: GitHub Pages Deploy (depends on Phases 2-3 for asset paths)
  - Fix absolute paths to relative
  - GitHub Actions workflow
  - Verify hash routing works on Pages
  - Tests: smoke test on deployed URL
```

**Why this order:**

1. **Pipeline first** because both coloring and dress-up need the new art assets. Without assets, you cannot test the frontend changes.
2. **Coloring before dress-up** because coloring is the bigger architectural change (SVG regions -> canvas flood fill). Dress-up is mostly swapping art assets into an existing mechanism.
3. **Deploy last** because it requires all asset paths to be finalized and all features working. Deploying a half-working app is worse than not deploying.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Runtime AI Generation
**What:** Calling OpenAI API from the frontend or FastAPI at runtime to generate art on demand.
**Why bad:** 10-30 second generation time. Costs money per image. Network dependency for a kids app. A 6-year-old will not wait.
**Instead:** Pre-generate all art during development. Commit static SVGs to the repo.

### Anti-Pattern 2: Server-Side Flood Fill
**What:** Sending the canvas image to a backend for flood fill processing.
**Why bad:** Network latency makes coloring feel laggy. Requires a running server (breaks static deployment). Unnecessary -- flood fill runs perfectly in the browser.
**Instead:** Client-side canvas flood fill. The algorithm is ~100 lines of JS.

### Anti-Pattern 3: Trying to Auto-Segment AI Art into data-regions
**What:** Writing code to automatically detect and tag semantic regions in AI-generated SVGs (the tail, the hair, etc.) to preserve the current fillRegion approach.
**Why bad:** This is a hard computer vision problem. The AI art has no semantic boundaries that align with what a 6-year-old considers "the tail" vs "the body." It is fragile, error-prone, and the wrong abstraction.
**Instead:** Use flood fill. It works with any image. The 6-year-old taps inside a closed area and it fills. No semantic understanding needed.

### Anti-Pattern 4: Building a Custom Bundler for GitHub Pages
**What:** Adding webpack/vite/parcel to bundle the vanilla JS for deployment.
**Why bad:** The app works without a bundler. Adding one creates configuration complexity, build failures, and debugging difficulty for zero user-facing benefit.
**Instead:** Deploy the `frontend/` directory as-is. ES modules work natively in all target browsers (iPad Safari 15+).

### Anti-Pattern 5: Generating One Large Image and Trying to Cut It Up
**What:** Generating a single "complete mermaid" image from the AI and trying to programmatically separate tail, hair, and accessories.
**Why bad:** Image segmentation is unreliable. Parts overlap. Cut boundaries look jagged. The whole approach is fragile.
**Instead:** Generate each variant part as a separate image with a clean white/transparent background. Each becomes its own SVG.

## Scalability Considerations

| Concern | Current (v1.0) | After v1.1 | Notes |
|---------|-----------------|------------|-------|
| Asset size | ~30KB total SVGs | ~200-500KB (AI-traced SVGs are larger) | Still fine. Pre-cache on first load. |
| Canvas memory | No canvas usage | 1024x1024 canvas for coloring (~4MB) | Well within iPad Safari's ~16MP limit |
| Flood fill perf | N/A | ~20-50ms per fill on iPad | Iterative span fill is fast enough |
| Deploy | Manual (uvicorn) | Automatic (GitHub Pages) | Push to main = live |
| Art generation | N/A (hand-drawn) | ~$0.20/image, 10-30s/image | Dev-time cost only |
| Test coverage | 37 Playwright E2E | Need updated tests for new interactions | Coloring tests need full rewrite |

## Sources

- [OpenAI Image Generation API](https://developers.openai.com/api/docs/guides/image-generation/) -- gpt-image-1 and gpt-image-1.5 API reference (HIGH confidence)
- [OpenAI Cookbook: Generate Images with GPT Image](https://cookbook.openai.com/examples/generate_images_with_gpt_image) -- Python code examples (HIGH confidence)
- [vtracer GitHub repository](https://github.com/visioncortex/vtracer) -- SVG output structure, configuration options (HIGH confidence)
- [vtracer Core Functionality (DeepWiki)](https://deepwiki.com/visioncortex/vtracer/7-core-functionality) -- stacked vs cutout mode details (MEDIUM confidence)
- [Canvas Flood Fill Algorithms (Codeheir)](https://codeheir.com/blog/2022/08/21/comparing-flood-fill-algorithms-in-javascript/) -- span fill vs recursive comparison (MEDIUM confidence)
- [Instant Flood Fill with HTML Canvas](https://shaneosullivan.wordpress.com/2023/05/23/instant-colour-fill-with-html-canvas/) -- pre-processing optimization technique (MEDIUM confidence)
- [floodfill.js library](https://github.com/binarymax/floodfill.js/) -- reference implementation (MEDIUM confidence)
- [SPA GitHub Pages](https://github.com/rafgraph/spa-github-pages) -- 404.html routing technique (MEDIUM confidence, but not needed since hash routing is used)
- [GitHub Pages SPA Discussion](https://github.com/orgs/community/discussions/64096) -- confirms hash routing works without workarounds (MEDIUM confidence)
- [OpenAI DALL-E 3 deprecation notice](https://platform.openai.com/docs/models/gpt-image-1) -- DALL-E 3 deprecated May 2026, use gpt-image-1 (HIGH confidence)
- Direct codebase analysis of existing v1.0 implementation (HIGH confidence)
