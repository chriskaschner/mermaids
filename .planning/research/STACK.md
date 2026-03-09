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
