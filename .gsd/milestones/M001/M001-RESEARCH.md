# Research Summary: v1.1 Art & Deploy

**Domain:** Integration of AI art pipeline, flood-fill coloring, and static deployment into existing kids creative web app
**Researched:** 2026-03-09
**Overall confidence:** HIGH

## Executive Summary

The v1.1 milestone adds three capabilities to the existing Mermaid Create & Play app: AI-generated kawaii art (replacing hand-crafted SVGs), canvas-based flood-fill coloring (replacing SVG region-based tap-to-fill), and GitHub Pages deployment (replacing FastAPI-only serving). After thorough analysis of the existing codebase (2,172 LOC, 37 Playwright tests, 5 JS modules, 1 Python pipeline module) and the target features, the integration path is clear but requires careful sequencing.

The biggest architectural change is in coloring. The v1.0 coloring system uses hand-tagged `<g data-region="tail">` SVG groups that get their `fill` attribute changed on tap. This does not work with AI-generated art because traced SVGs produce hundreds of stacked paths with no semantic grouping. The solution is a hybrid canvas+SVG architecture: render line art SVG onto a `<canvas>` for flood-fill pixel operations, overlay the original SVG with `pointer-events: none` to keep line art crisp. This is a well-established pattern (Microsoft's Windows Coloring Book sample app uses the same layered approach).

The dress-up system is architecturally sound for the transition. The `<defs>` + `<use>` variant swap pattern (change `href` attribute to swap parts) works identically regardless of whether the art inside `<defs>` is hand-drawn or AI-generated. The challenge is producing AI art that fits the convention: each variant as a separate generation, spatially aligned, wrapped in `<g id="tail-1">` groups by a post-processing pipeline. The recoloring system (set all fills to one color) maps naturally to kawaii flat-color style.

GitHub Pages deployment is trivial given the existing architecture. Hash routing already works (the browser never sends hash fragments to the server). The only code change is fixing one absolute fetch path in `app.js` (`/assets/svg/mermaid.svg` -> `assets/svg/mermaid.svg`). No build step is needed -- the `frontend/` directory deploys as-is.

The art generation pipeline is the highest-risk component. AI image consistency across separate generations is unreliable. The recommended approach: generate a full reference character, then use OpenAI's edit API with masks to create variants of specific regions (different tails, different hairstyles). Use gpt-image-1 (not DALL-E 3, which is deprecated May 2026). All generation happens offline at dev time; assets are committed as static files.

## Key Findings

**Stack:** Existing stack is correct. Add openai Python package for pipeline, canvas flood-fill in vanilla JS. No new frontend dependencies. gpt-image-1 replaces deprecated DALL-E 3.

**Architecture:** Hybrid canvas+SVG for coloring (biggest change). Dress-up defs+use pattern preserved. Pipeline produces static assets committed to repo. GitHub Pages serves frontend/ directory with zero build step.

**Critical pitfall:** Canvas memory limits on iPad Safari. Must release canvas resources when navigating away from coloring pages. Single shared canvas, never create-per-page.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Art Pipeline** - Build the offline pipeline first (generate.py + trace.py updates + assemble.py)
   - Addresses: AI art generation, kawaii style, SVG asset production
   - Avoids: Building frontend features without assets to test against
   - This phase can be tested with Python unit tests alone, no browser needed

2. **Flood-Fill Coloring Refactor** - Replace SVG region coloring with canvas flood fill
   - Addresses: Coloring pages that work with any AI-generated art
   - Avoids: Manual region tagging (impossible to maintain with AI art)
   - Depends on: Phase 1 for coloring page SVGs to test against
   - Biggest code change: coloring.js rewrite + floodfill.js new module + app.js openColoringPage changes

3. **Dress-Up Art Swap** - Replace hand-crafted mermaid.svg with AI-generated version
   - Addresses: Kawaii art style for dress-up
   - Avoids: Major code changes (mechanism is unchanged, only art and PARTS IDs change)
   - Depends on: Phase 1 for mermaid SVG assets

4. **GitHub Pages Deployment** - Static deployment + path fixes
   - Addresses: Accessibility on iPad (no need to run FastAPI)
   - Avoids: Breaking tests (keep FastAPI for dev/test)
   - Depends on: Phases 2-3 (all features must work before deploying)

**Phase ordering rationale:**
- Pipeline must come first because both coloring and dress-up need the new art assets
- Coloring before dress-up because coloring is the larger architectural change (new module, rewritten module, canvas layer)
- Dress-up after coloring because it is mostly art-swap with minimal code changes
- Deploy last because deploying a broken app is worse than not deploying

**Research flags for phases:**
- Phase 1 (Art Pipeline): Likely needs deeper research on prompt engineering for consistent kawaii style, and on gpt-image-1 edit API with masks for variant generation
- Phase 2 (Flood Fill): Standard patterns, good reference implementations available. The canvas+SVG overlay is well-understood. Tolerance tuning (anti-aliasing handling) may need iteration.
- Phase 3 (Dress-Up): Low risk. The defs+use mechanism is proven. Risk is in art asset quality, not code.
- Phase 4 (Deploy): Standard GitHub Pages setup. No research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack is correct; only addition is openai Python package |
| Features | HIGH | All features are well-understood patterns (flood fill, SVG variants, static deploy) |
| Architecture | HIGH | Direct codebase analysis + established patterns (canvas flood fill, SVG defs+use) |
| Pitfalls | HIGH | Verified against official docs (Apple canvas limits, OpenAI API deprecations, GitHub Pages behavior) |
| Art Pipeline | MEDIUM | AI art consistency is inherently unpredictable; edit API approach is recommended but needs validation |

## Gaps to Address

- **Prompt engineering specifics.** What exact prompts produce consistent kawaii mermaid art with clean outlines suitable for tracing? This requires empirical iteration, not research.
- **gpt-image-1 edit API with masks.** Confirmed available but not deeply tested for the specific use case of "keep this character, regenerate only the tail region." Phase-specific research recommended.
- **vtracer settings for AI art.** The current `simplify=True` binary mode works for hand-drawn art. AI-generated images with more detail may need different `filter_speckle`, `color_precision`, and `layer_difference` values. Empirical tuning needed.
- **Canvas flood-fill performance on older iPads.** The algorithm is fast in theory (~20-50ms for 1024x1024) but real-world performance depends on iPad model. Test on actual hardware early.

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

# Technology Stack: v1.1 Additions

**Project:** Mermaid Create & Play -- v1.1 Art & Deploy
**Researched:** 2026-03-09
**Scope:** NEW capabilities only (AI art generation, flood-fill coloring, GitHub Pages deployment)

## Existing Stack (validated, not changing)

FastAPI + vanilla JS, no framework, no build step. SVG rendering with vtracer. Pointer event delegation. SVG defs+use for dress-up. Playwright E2E testing. uv for Python packaging. Hash-based SPA router (`#/home`, `#/dressup`, `#/coloring`).

---

## New Stack Additions

### 1. AI Art Generation Pipeline

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| openai (Python SDK) | >=2.26 | Call OpenAI Images API | Official SDK, handles auth, retries, base64 decoding. v2.26.0 released 2026-03-05. | HIGH |
| gpt-image-1 (model) | -- | Generate kawaii mermaid art | Best balance of quality vs cost for illustration. gpt-image-1.5 exists but costs 2x more and quality difference is marginal for traced SVG output. gpt-image-1-mini is too low quality for art assets. | MEDIUM |

**API Endpoint:** `POST /v1/images/generations` via `client.images.generate()`

**Complete generation call:**

```python
from openai import OpenAI
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO

client = OpenAI()  # reads OPENAI_API_KEY from environment

result = client.images.generate(
    model="gpt-image-1",
    prompt="kawaii mermaid with long flowing hair, cute chibi style, clean lines, white background, illustration suitable for coloring book",
    size="1024x1024",
    quality="high",
    output_format="png",
    background="transparent",  # PNG only -- useful for dress-up parts
    n=1,
)

image_bytes = base64.b64decode(result.data[0].b64_json)
image = Image.open(BytesIO(image_bytes))
image.save("output.png")
```

**Key parameters:**

| Parameter | Options | Recommendation | Why |
|-----------|---------|----------------|-----|
| model | gpt-image-1, gpt-image-1.5, gpt-image-1-mini | gpt-image-1 | Quality sweet spot. $0.011-0.167/image at 1024x1024. |
| size | 1024x1024, 1024x1536, 1536x1024 | 1024x1024 | Square input works best for vtracer. Dress-up parts and coloring pages both work square. |
| quality | low, medium, high | high for coloring pages, medium for dress-up parts | Coloring pages need clean lines. Dress-up parts get traced anyway. |
| output_format | png, jpeg, webp | png | Transparency support needed for dress-up parts. Lossless for clean tracing input. |
| background | transparent, opaque | transparent for parts, opaque for coloring pages | Dress-up parts need transparent background for layering. |
| n | 1-10 | 1 | Generate one at a time, review, iterate on prompt. |

**Cost estimate for full asset set:**
- ~15 coloring pages at high quality: ~15 x $0.167 = ~$2.50
- ~20 dress-up parts at medium quality: ~20 x $0.034 = ~$0.68
- Iteration/rejects (3x multiplier): ~$9.54
- **Total: ~$10-15 for complete asset library**

**IMPORTANT: gpt-image-1 vs DALL-E 3 decision.** DALL-E 2 and DALL-E 3 are deprecated with support ending 2026-05-12. Use gpt-image-1 exclusively. Do not use DALL-E models.

**Integration with existing pipeline:** The generation script is an offline CLI tool (not a runtime API endpoint). It generates PNG files that feed into the existing `trace.py` vtracer pipeline. The flow is:

```
[gpt-image-1 API] --> PNG file --> [Pillow preprocessing] --> [vtracer trace_to_svg()] --> SVG file --> [manual region tagging] --> frontend asset
```

**What to add to pyproject.toml:**

```bash
# Add as optional pipeline dependency (not needed at runtime)
uv add --optional pipeline openai
```

### 2. Flood-Fill Coloring on Traced SVGs

**The core decision: Canvas overlay flood fill vs SVG path-based fill.**

The existing v1.0 coloring uses SVG path-based fill -- tapping a `<g data-region="...">` element sets `fill` on child paths. This requires manually tagging regions in SVG markup. For AI-generated/traced art, manual region tagging is the bottleneck.

**Recommendation: Canvas overlay with pre-computed masks.** Use a hidden canvas to render the SVG, pre-compute fillable regions via flood fill at load time, then apply fills instantly on tap.

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| SVG path-based (current) | Instant fill, native hit detection, undo is trivial | Requires manual `data-region` tagging on every SVG path. Breaks the automated pipeline. | REJECT for new art |
| Canvas flood fill (per-tap) | Works on any image, no manual tagging | Slow on large images (blocks UI). Anti-aliased edge bleeding. Bad on iPad. | REJECT |
| Canvas pre-computed masks | Instant fill after initial load. Works on any traced SVG. No manual tagging. | Requires Web Worker for preprocessing. ~200-500ms load time. More code than path-based. | USE THIS |
| Hybrid (SVG outlines + canvas fill layer) | Clean separation of concerns | Complex layer management, z-ordering issues | OVERCOMPLICATED |

**Pre-computed mask technique (from Kidz Fun Art / Shane O'Sullivan):**

1. At page load, render the coloring page SVG onto a hidden canvas
2. In a Web Worker, scan all pixels. For each unvisited pixel, run iterative flood fill to identify the enclosed region. Assign each region a unique ID (stored in alpha channel or separate mask array)
3. Store masks as `Uint8Array` -- one mask per fillable region
4. On user tap: look up which region the tap coordinates fall in, draw that mask in the selected color using `globalCompositeOperation = "source-in"`
5. Composite the colored mask onto the visible canvas, with the SVG outlines drawn on top

**Implementation -- no external library needed.** The flood fill algorithm is ~80 lines of iterative JavaScript. Using a library like `floodfill.js` or `FloodFill2D` is unnecessary overhead for this use case. Write a focused implementation:

```javascript
// Iterative flood fill -- no stack overflow risk
function floodFill(imageData, startX, startY, tolerance) {
  const { data, width, height } = imageData;
  const stack = [[startX, startY]];
  const visited = new Uint8Array(width * height);
  const mask = [];

  const startIdx = (startY * width + startX) * 4;
  const startR = data[startIdx], startG = data[startIdx+1],
        startB = data[startIdx+2], startA = data[startIdx+3];

  while (stack.length > 0) {
    const [x, y] = stack.pop();
    const pixelIdx = y * width + x;
    if (visited[pixelIdx]) continue;

    const idx = pixelIdx * 4;
    const dr = Math.abs(data[idx] - startR);
    const dg = Math.abs(data[idx+1] - startG);
    const db = Math.abs(data[idx+2] - startB);

    if (dr + dg + db > tolerance) continue;

    visited[pixelIdx] = 1;
    mask.push(pixelIdx);

    if (x > 0) stack.push([x-1, y]);
    if (x < width-1) stack.push([x+1, y]);
    if (y > 0) stack.push([x, y-1]);
    if (y < height-1) stack.push([x, y+1]);
  }
  return mask;
}
```

**Key implementation details:**

| Concern | Solution |
|---------|----------|
| Performance on iPad | Web Worker for preprocessing. Main thread stays responsive. |
| Anti-aliased edge bleeding | Set tolerance=30-50. vtracer output has clean edges (vector-traced), so anti-aliasing is minimal after re-rasterization. |
| Undo support | Store previous mask colors in undo stack (same pattern as current coloring.js). |
| Canvas size for iPad Safari | Keep canvas under 4096x4096 (16MP limit). 1024x1024 is safe. |
| Touch coordinate mapping | Use `canvas.getBoundingClientRect()` to map pointer event coordinates to canvas pixel coordinates. |
| SVG outline on top | Draw SVG outlines on a separate canvas layer (or re-draw on top after each fill). Outlines stay crisp and unfilled. |
| Retina display | Set canvas dimensions to `devicePixelRatio * CSS dimensions`. Scale context accordingly. |

**What NOT to add:**

| Library | Why Not |
|---------|---------|
| floodfill.js | Unmaintained (no recent commits). Adds global window pollution. 80 lines of custom code is cleaner. |
| FloodFill2D | Over-featured (gradients, compositing, cut/copy). Only 15 GitHub stars. We need basic solid fill only. |
| Fabric.js / Konva.js | Canvas abstraction libraries. Massive overhead for a single flood-fill feature. |

**Integration with existing coloring.js:**

The existing `coloring.js` exports `fillRegion(regionGroup, color)` which operates on SVG DOM elements. For the new canvas-based approach, this function signature changes. The coloring module needs a new implementation:

- `initColoringCanvas(svgUrl)` -- load SVG, render to canvas, precompute masks in Worker
- `fillRegionAtPoint(x, y, color)` -- look up mask at coordinates, apply fill
- `undo()` -- same pattern, restore previous canvas state
- `getSelectedColor()` / `setSelectedColor()` -- unchanged

The existing SVG path-based coloring can remain as a fallback for the v1.0 hand-crafted SVGs. The new canvas-based approach applies to AI-generated coloring pages.

### 3. GitHub Pages Static Deployment

**The architectural shift:** The app currently runs FastAPI serving static files. For GitHub Pages, we need a pure static site -- no Python server at runtime.

**This is simpler than it sounds.** The existing app is already a static site in practice:
- `frontend/index.html` -- single HTML file
- `frontend/js/*.js` -- vanilla JS modules
- `frontend/css/style.css` -- single stylesheet
- `frontend/assets/` -- SVG/image assets
- No API endpoints are used at runtime (no `/api/...` calls)
- No Jinja2 templating (despite being in the v1.0 STACK.md, it was never actually used)
- No server-side rendering

The only change needed: assets currently fetched with paths like `assets/svg/mermaid.svg` (already relative in the coloring module) and `/assets/svg/mermaid.svg` (absolute in the dress-up fetch). On GitHub Pages project sites, the URL is `https://username.github.io/mermaids/`, so absolute paths break.

**Solution: Use relative paths everywhere.**

| Current Path | GitHub Pages Path | Fix |
|--------------|-------------------|-----|
| `/assets/svg/mermaid.svg` | `assets/svg/mermaid.svg` | Remove leading `/` in dressup fetch |
| `assets/svg/coloring/page-1-ocean.svg` | Same | Already relative, works as-is |
| `css/style.css` | Same | Already relative in HTML link tag |
| Hash routes `#/home` | `#/home` | Hash routing works as-is (no server involvement) |

**Deployment method: GitHub Actions workflow (official `actions/deploy-pages`).**

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| actions/checkout | v5 | Check out repo | Standard |
| actions/configure-pages | v5 | Set up Pages | Required by deploy-pages |
| actions/upload-pages-artifact | v4 | Bundle static files | Required (v3 deprecated Jan 2025) |
| actions/deploy-pages | v4 | Deploy to Pages | Official GitHub action |

**Workflow file: `.github/workflows/deploy.yml`**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v4
        with:
          path: frontend

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Key detail:** The `path: frontend` in `upload-pages-artifact` deploys only the `frontend/` directory, not the entire repo. This means Python code, tests, and pipeline scripts are NOT deployed. The site URL becomes `https://username.github.io/mermaids/` and serves `frontend/index.html` as the root.

**GitHub Pages configuration (one-time setup in repo Settings):**
1. Settings > Pages > Source: "GitHub Actions" (not "Deploy from a branch")
2. No custom domain needed (but supported)
3. Repo must be Public (or on GitHub Pro/Team for private repo Pages)

**Hash routing works natively on GitHub Pages.** No 404.html redirect hack needed. The app uses `#/home`, `#/dressup`, `#/coloring` -- hash fragments are never sent to the server, so GitHub Pages always serves `index.html` regardless of the hash. This is the simplest SPA routing approach and it is already implemented.

**What NOT to add:**

| Technology | Why Not |
|------------|---------|
| gh-pages npm package | Requires npm/Node.js. The project has no JS build tooling. |
| Jekyll | GitHub Pages default. Unnecessary -- we have plain HTML. Add `.nojekyll` file to skip Jekyll processing. |
| 404.html SPA redirect | Only needed for path-based routing (`/dressup`, `/coloring`). Hash routing (`#/dressup`) does not need this. |
| Custom domain | Not needed for MVP. Can add later via CNAME file. |
| Service Worker / PWA | Nice for offline but adds complexity. Defer to v2. |

**Add `.nojekyll` to `frontend/`:** An empty file that tells GitHub Pages to skip Jekyll processing. Without it, files starting with `_` would be ignored and build times are slower.

---

## Deployment Architecture Change

```
BEFORE (v1.0):                          AFTER (v1.1):

[iPad Safari]                           [iPad Safari]
    |                                       |
    | localhost:8000                         | HTTPS
    |                                       |
[FastAPI + Uvicorn]                     [GitHub Pages CDN]
    |                                       |
    |-- Static files (frontend/)            |-- index.html
    |                                       |-- js/*.js
                                            |-- css/style.css
                                            |-- assets/svg/*.svg

[Developer machine]                     [Developer machine]
    |                                       |
    |-- FastAPI (dev server)                |-- FastAPI (dev server, local testing)
    |-- pipeline/ (art generation)          |-- pipeline/ (art generation, offline)
    |-- vtracer (SVG tracing)               |-- vtracer (SVG tracing, offline)
    |-- openai SDK (image gen)              |-- openai SDK (image gen, offline)
```

The server-side stack (FastAPI, vtracer, openai, Pillow) becomes a **development-only toolchain** for generating assets. The production deployment is pure static files on GitHub Pages.

FastAPI remains useful for local development (serving files with live reload, testing) but is not needed in production.

---

## Complete New Dependencies

### Python (dev/pipeline only -- not deployed)

```bash
# Add OpenAI SDK for art generation pipeline
uv add --optional pipeline openai

# Existing deps (no changes)
# fastapi, uvicorn, vtracer, pillow -- already in pyproject.toml
```

### Frontend (zero new dependencies)

No npm packages. No build tools. The flood-fill implementation is ~80-120 lines of vanilla JS plus a ~40-line Web Worker script. All browser-native APIs:
- `Canvas 2D API` -- rendering, compositing
- `Web Workers API` -- background mask computation
- `ImageData` -- pixel manipulation
- `OffscreenCanvas` -- render SVG in Worker (Safari 16.4+, iPad supported)

### GitHub Actions (CI/CD only)

```yaml
# In .github/workflows/deploy.yml
actions/checkout@v5
actions/configure-pages@v5
actions/upload-pages-artifact@v4
actions/deploy-pages@v4
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Image gen model | gpt-image-1 | gpt-image-1.5 | 2x cost, marginal quality gain for traced output. Art gets vectorized anyway. |
| Image gen model | gpt-image-1 | gpt-image-1-mini | Too low quality. Kawaii art needs clean lines and detail. |
| Image gen model | gpt-image-1 | Stable Diffusion (local) | Requires GPU, complex setup, model downloads. OpenAI API is pay-per-use with zero infrastructure. |
| Image gen model | gpt-image-1 | Midjourney | No programmatic API. Manual Discord workflow. Cannot automate. |
| Flood fill | Custom iterative JS | floodfill.js library | Unmaintained, global window pollution, only 51 commits. Custom code is cleaner. |
| Flood fill | Custom iterative JS | FloodFill2D library | Over-engineered (gradients, compositing, cut/copy). 15 stars. We need solid fill only. |
| Flood fill | Canvas pre-computed masks | SVG path-based (current approach) | Requires manual `data-region` tagging. Breaks automated pipeline from AI art. |
| Flood fill | Canvas pre-computed masks | Per-tap flood fill | Slow on large images (100ms+). Anti-aliased edge bleeding. Blocks main thread. |
| Deployment | GitHub Pages + Actions | Netlify | More features but unnecessary. GitHub Pages is free, integrated, zero-config for static. |
| Deployment | GitHub Pages + Actions | Vercel | Same as Netlify -- overkill for static files. |
| Deployment | GitHub Pages + Actions | AWS S3 + CloudFront | Infrastructure overhead. GitHub Pages is free and simpler. |
| Deployment | GitHub Actions workflow | gh-pages branch | Actions workflow is cleaner, no orphan branch, official GitHub approach since 2022. |
| SPA routing | Hash routing (existing) | Path-based + 404.html redirect | Hash routing already works. No reason to change. Path-based adds complexity and SEO hacks. |

---

## Safari/iPad Compatibility Notes for New Features

| Feature | Safari Concern | Mitigation | Confidence |
|---------|----------------|------------|------------|
| Web Worker | Supported since Safari 7 | No concern | HIGH |
| OffscreenCanvas | Supported since Safari 16.4 (2023) | iPadOS 16.4+. If targeting older iPads, use main-thread canvas render instead. | MEDIUM |
| Canvas getImageData | Supported, but cross-origin restrictions apply | SVG is same-origin (loaded from same domain). No CORS issues. | HIGH |
| Canvas 4096x4096 limit | iPad Safari caps at ~16MP canvas | Use 1024x1024 canvas for coloring pages. Well under limit. | HIGH |
| ES modules in Worker | Supported since Safari 15 | Use `new Worker('worker.js', { type: 'module' })` | HIGH |
| GitHub Pages HTTPS | Required by Safari for Service Workers (future) | GitHub Pages serves HTTPS by default | HIGH |

---

## Installation Summary

```bash
# One new Python dependency (pipeline/dev only)
uv add --optional pipeline openai

# Set OpenAI API key for art generation
export OPENAI_API_KEY="sk-..."

# Frontend: still zero JS dependencies
# GitHub Actions: configured via .github/workflows/deploy.yml (no install needed)

# New file to create:
touch frontend/.nojekyll
```

---

## Sources

- [OpenAI Image Generation Guide](https://developers.openai.com/api/docs/guides/image-generation/) -- API parameters, model options (HIGH confidence)
- [OpenAI Cookbook: Generate Images with GPT Image](https://developers.openai.com/cookbook/examples/generate_images_with_gpt_image) -- Python SDK usage (HIGH confidence)
- [OpenAI API Reference: Images](https://platform.openai.com/docs/api-reference/images) -- Endpoint specification (HIGH confidence)
- [OpenAI Pricing](https://openai.com/api/pricing/) -- Cost per image by model/quality/size (HIGH confidence)
- [openai PyPI](https://pypi.org/project/openai/) -- v2.26.0 released 2026-03-05, Python >=3.9 (HIGH confidence)
- [GPT Image 1 Model](https://platform.openai.com/docs/models/gpt-image-1) -- Model capabilities, DALL-E deprecation notice (HIGH confidence)
- [GPT Image 1.5 Model](https://platform.openai.com/docs/models/gpt-image-1.5) -- Newer model comparison (HIGH confidence)
- [Instant Colour Fill with HTML Canvas](https://shaneosullivan.wordpress.com/2023/05/23/instant-colour-fill-with-html-canvas/) -- Pre-computed mask technique for coloring apps (MEDIUM confidence)
- [Comparing Flood Fill Algorithms in JavaScript](https://codeheir.com/blog/2022/08/21/comparing-flood-fill-algorithms-in-javascript/) -- Algorithm comparison, recursive vs iterative (MEDIUM confidence)
- [An HTML5 Canvas Flood Fill That Doesn't Kill the Browser](https://ben.akrin.com/an-html5-canvas-flood-fill-that-doesnt-kill-the-browser/) -- Performance-optimized iterative approach (MEDIUM confidence)
- [floodfill.js](https://github.com/binarymax/floodfill.js/) -- Canvas flood fill library, evaluated and not recommended (HIGH confidence)
- [FloodFill2D](https://github.com/blindman67/FloodFill2D) -- Advanced flood fill library, evaluated and not recommended (HIGH confidence)
- [GitHub Pages: Using Custom Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) -- Official Actions deployment docs (HIGH confidence)
- [actions/deploy-pages](https://github.com/actions/deploy-pages) -- Official deploy action, v4 (HIGH confidence)
- [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact) -- v4 required, v3 deprecated Jan 2025 (HIGH confidence)
- [SPA GitHub Pages](https://github.com/rafgraph/spa-github-pages) -- 404.html redirect technique, evaluated and not needed for hash routing (HIGH confidence)
- [vtracer GitHub](https://github.com/visioncortex/vtracer) -- Stacked vs cutout hierarchical modes (HIGH confidence)
- [vtracer DeepWiki](https://deepwiki.com/visioncortex/vtracer) -- Core functionality and path tracing details (MEDIUM confidence)
- [GitHub Pages Relative Paths](https://www.codestudy.net/blog/github-pages-and-relative-paths/) -- Base URL / subdirectory path issues (HIGH confidence)

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