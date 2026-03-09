# Phase 1: Foundation - Research

**Researched:** 2026-03-09
**Domain:** SVG rendering, touch interaction, art pipeline, vanilla JS SPA, FastAPI static serving
**Confidence:** MEDIUM-HIGH

## Summary

Phase 1 establishes the entire rendering and interaction pipeline: a FastAPI backend serves a vanilla JS single-page application that displays an inline SVG mermaid with watercolor styling, responds to touch on iPad Safari, and provides navigation between activity screens. The biggest technical risks are (1) the AI-image-to-SVG conversion pipeline producing clean, interactive SVG and (2) reliable touch event handling on SVG elements in iPad Safari.

The recommended approach is hash-based client-side routing (simplest, no server catch-all needed), inline SVG with `<g>` groups for tappable regions, pointer events for interaction control, CSS `@keyframes` for sparkle feedback, and SVG filters (`feTurbulence` + `feDisplacementMap`) for watercolor texture effects. The art pipeline should use vtracer (Python package, v0.6.12) for raster-to-SVG conversion, with AI-generated source images processed through it.

**Primary recommendation:** Start with the art pipeline prototype (AI image -> vtracer -> clean SVG with named groups) because it is the highest-risk unknown and everything else depends on having a working SVG asset.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Generate watercolor mermaid art using AI image tools, then trace/convert raster images to SVG
- Tool selection is flexible -- try multiple AI tools (Midjourney, DALL-E, Claude, etc.) and pick what produces the best results
- For Phase 1, create a simple mermaid silhouette divided into tappable regions (tail, hair, body) -- proves the SVG + touch pipeline works without needing final art
- Detailed, polished art and swappable parts are Phase 2 concerns -- Phase 1 validates the pipeline
- Sparkle/shimmer particle effect on tapped regions, fading after ~0.5s
- Very forgiving tap detection: expand hit areas beyond visible SVG boundaries, snap to nearest region for imprecise child taps
- All interactive elements maintain 60pt+ tap targets per FOUN-01
- Vanilla JS + FastAPI decided at project level (no framework, no build step)
- SVG-first rendering for all interactive content

### Claude's Discretion
- Watercolor art style direction (balance 6-year-old appeal with what traces cleanly to SVG)
- Whether background taps produce subtle feedback (e.g., water ripple) or only mermaid regions respond
- Sparkle color approach (consistent gold/white vs region-matched colors)
- Home screen layout and navigation icon placement (not discussed -- standard approaches fine)
- SVG tracing tool selection and optimization

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUN-01 | All tap targets are 60pt+ for a 6-year-old's motor control | SVG pointer-events with invisible expanded hit areas; CSS min-width/min-height on interactive `<g>` groups; see "Expanded Hit Areas" pattern |
| FOUN-02 | App works in iPad Safari with touch interaction | touch-action: manipulation; pointer events on SVG; viewport meta tag; see "iPad Safari Touch Events" section |
| FOUN-03 | Consistent watercolor art style across all assets | SVG filters (feTurbulence + feDisplacementMap) for watercolor texture; vtracer for consistent tracing; see "Watercolor SVG Filters" pattern |
| FOUN-04 | All interactions provide instant visual feedback (no loading states) | CSS @keyframes sparkle animation; inline SVG attribute changes on touch; no network calls during interaction |
| NAVG-01 | Home screen shows dress-up and coloring as large icon buttons (no text required) | Hash-based routing; large SVG icon buttons; see "Navigation Shell" pattern |
| NAVG-02 | User can switch between activities from any screen via icon navigation | Persistent nav bar component; hash change listener; see "Navigation Shell" pattern |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Backend server, static file serving | Project decision (user preference for Python); StaticFiles with html=True serves the SPA |
| uvicorn | 0.34+ | ASGI server | Standard FastAPI companion; production-ready |
| vtracer | 0.6.12 | Raster image to SVG conversion | Python bindings, handles full-color images (unlike Potrace which is B&W only), O(n) algorithm |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pillow | 11+ | Image preprocessing before SVG tracing | Resize, crop, adjust contrast of AI-generated images before passing to vtracer |
| pytest | 8+ | Python test framework | All backend tests and pipeline validation |
| playwright | 1.49+ | Browser automation testing | E2E tests with WebKit/iPad emulation for touch interaction validation |
| pytest-playwright | 0.6+ | Pytest plugin for Playwright | Integrates Playwright into pytest test runner |
| httpx | 0.28+ | Async HTTP client | Required by FastAPI TestClient for API tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| vtracer | Potrace | Potrace is B&W only -- cannot handle colored watercolor art; vtracer handles full-color high-res images |
| vtracer | Vectorizer.AI (online) | Online tool is manual, not scriptable; vtracer is a Python package that integrates into the pipeline |
| vtracer | Recraft AI Vectorizer | Online-only, no API for automation; good for manual comparison during art exploration |
| Hash routing | History API routing | History API requires server-side catch-all route; hash routing works purely client-side with zero server config |
| Hand-rolled sparkle | particles.js / sparticles | External libraries are overkill for a simple sparkle-on-tap effect; 10-20 lines of CSS @keyframes handles it |

**Installation:**
```bash
uv add fastapi uvicorn vtracer pillow
uv add --dev pytest playwright pytest-playwright httpx
uv run playwright install webkit
```

## Architecture Patterns

### Recommended Project Structure
```
mermaids/
├── pyproject.toml
├── src/
│   └── mermaids/
│       ├── __init__.py
│       ├── app.py              # FastAPI app, static mount
│       └── pipeline/
│           ├── __init__.py
│           └── trace.py        # vtracer wrapper for SVG conversion
├── frontend/
│   ├── index.html              # SPA shell with router
│   ├── css/
│   │   └── style.css           # All styles including sparkle animations
│   ├── js/
│   │   ├── app.js              # Router, view management
│   │   ├── touch.js            # Touch/pointer event handling
│   │   └── sparkle.js          # Sparkle particle effect
│   └── assets/
│       └── svg/
│           └── mermaid.svg     # Traced SVG with named groups
├── assets/
│   └── source/                 # AI-generated source images (raster)
└── tests/
    ├── test_app.py             # FastAPI endpoint tests
    ├── test_pipeline.py        # SVG tracing pipeline tests
    └── test_e2e.py             # Playwright iPad emulation tests
```

### Pattern 1: Hash-Based SPA Router
**What:** Client-side routing using `window.location.hash` and the `hashchange` event. URLs look like `/#/home`, `/#/dressup`, `/#/coloring`.
**When to use:** Always -- this is the navigation foundation.
**Example:**
```javascript
// Source: adapted from dev.to/dcodeyt vanilla JS SPA patterns
const routes = {
  '':        renderHome,
  'home':    renderHome,
  'dressup': renderDressUp,
  'coloring': renderColoring,
};

function router() {
  const hash = window.location.hash.slice(2) || 'home'; // strip '#/'
  const render = routes[hash] || renderHome;
  render();
  updateNavHighlight(hash);
}

window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', router);
```

### Pattern 2: SVG Touch Interaction with Expanded Hit Areas
**What:** Attach pointer/touch events to SVG `<g>` groups. Use invisible `<rect>` elements behind visible shapes to expand tap targets to 60pt+.
**When to use:** Every interactive SVG region (tail, hair, body).
**Example:**
```javascript
// Source: gomakethings.com event delegation + MDN pointer-events
// In the SVG, each tappable region is a <g> with a data attribute:
// <g data-region="tail" pointer-events="all">
//   <rect fill="none" x="..." y="..." width="80" height="80" /> <!-- hit area -->
//   <path d="..." fill="#..." />  <!-- visible art -->
// </g>

document.querySelector('#mermaid-svg').addEventListener('pointerdown', (e) => {
  const region = e.target.closest('[data-region]');
  if (!region) return;

  const regionName = region.dataset.region;
  triggerSparkle(region, e);
  provideFeedback(region);
});
```

### Pattern 3: CSS Sparkle Animation
**What:** Create sparkle particles as small SVG elements (stars/circles) animated with CSS @keyframes. Spawn on tap, fade after ~0.5s.
**When to use:** Visual feedback for FOUN-04 and the sparkle requirement.
**Example:**
```javascript
// Source: adapted from codepen sparkle patterns + Josh Comeau sparkle approach
function triggerSparkle(parentGroup, event) {
  const svg = document.querySelector('#mermaid-svg');
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());

  for (let i = 0; i < 6; i++) {
    const sparkle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    sparkle.setAttribute('cx', svgPt.x + (Math.random() - 0.5) * 40);
    sparkle.setAttribute('cy', svgPt.y + (Math.random() - 0.5) * 40);
    sparkle.setAttribute('r', 2 + Math.random() * 3);
    sparkle.setAttribute('fill', 'gold');
    sparkle.classList.add('sparkle');
    svg.appendChild(sparkle);

    setTimeout(() => sparkle.remove(), 600);
  }
}
```
```css
/* CSS @keyframes for sparkle */
.sparkle {
  animation: sparkle-fade 0.6s ease-out forwards;
  pointer-events: none;
}

@keyframes sparkle-fade {
  0% { opacity: 1; transform: scale(0); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0; transform: scale(0.5) translateY(-10px); }
}
```

### Pattern 4: Watercolor SVG Filters
**What:** Apply SVG filter primitives to create watercolor texture on SVG paths. Uses `feTurbulence` for organic noise and `feDisplacementMap` for edge softening.
**When to use:** Applied to the mermaid SVG to achieve the watercolor art style (FOUN-03).
**Example:**
```xml
<!-- Source: Codrops feTurbulence tutorial + CodePen watercolor examples -->
<svg>
  <defs>
    <filter id="watercolor" x="-10%" y="-10%" width="120%" height="120%">
      <!-- Generate organic noise -->
      <feTurbulence type="fractalNoise" baseFrequency="0.04"
                    numOctaves="4" seed="2" result="noise" />
      <!-- Soften edges with displacement -->
      <feDisplacementMap in="SourceGraphic" in2="noise"
                         scale="8" xChannelSelector="R" yChannelSelector="G"
                         result="displaced" />
      <!-- Add paper-like texture overlay -->
      <feTurbulence type="fractalNoise" baseFrequency="0.8"
                    numOctaves="3" result="fine-noise" />
      <feComposite in="displaced" in2="fine-noise"
                   operator="in" result="textured" />
    </filter>
  </defs>

  <g filter="url(#watercolor)">
    <!-- mermaid paths go here -->
  </g>
</svg>
```

### Pattern 5: FastAPI Static File Serving
**What:** Mount the frontend directory at root with `html=True` for SPA behavior.
**When to use:** The entire backend setup for Phase 1.
**Example:**
```python
# Source: FastAPI official docs + bugfactory.io pattern
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API routes go here (none needed for Phase 1, but structure for future)
# @app.get("/api/...")

# Mount frontend last -- catches all non-API routes
app.mount("/", StaticFiles(directory=Path("frontend"), html=True), name="frontend")
```

### Anti-Patterns to Avoid
- **Building a custom router library:** Hash-based routing is 20 lines of code. Do not introduce a routing library.
- **Using Canvas instead of SVG:** Canvas requires manual hit-testing, repainting, and loses DOM accessibility. SVG elements are DOM nodes with native event handling.
- **Adding a build step (webpack, vite, etc.):** Project decision is no build step. Vanilla JS with ES modules (type="module") works in modern Safari.
- **Using jQuery for DOM manipulation:** Completely unnecessary for this scope. Vanilla JS has everything needed.
- **Putting SVG in `<img>` tags or as CSS background:** Inline SVG is required for touch interaction on individual elements. External SVG references lose interactivity.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Raster-to-vector conversion | Custom image tracing | vtracer (Python package) | Decades of research in tracing algorithms; color handling is extremely complex |
| Image preprocessing | Custom resize/crop scripts | Pillow | Handles format conversion, resize, contrast adjustment reliably |
| HTTP server | Custom socket server | FastAPI + uvicorn | Production-grade ASGI with zero config |
| Browser testing | Manual iPad testing only | Playwright with WebKit emulation | Automated, repeatable, catches regressions; has iPad device profiles |
| SVG coordinate transforms | Manual math for screen-to-SVG coords | `svg.createSVGPoint()` + `getScreenCTM().inverse()` | Browser's native SVG coordinate API handles all transform edge cases |

**Key insight:** The art pipeline (AI image -> trace -> SVG) is the only truly novel piece. Everything else -- serving files, handling events, routing, animating -- uses well-established browser APIs. Don't over-engineer the plumbing.

## Common Pitfalls

### Pitfall 1: SVG Touch Events Not Firing in iPad Safari
**What goes wrong:** Touch/click events on SVG elements silently fail or fire on wrong targets.
**Why it happens:** (1) SVG elements with `fill="none"` don't receive pointer events by default. (2) Safari has a 300ms tap delay. (3) The `event.target` inside an SVG `<g>` group is the child `<path>`, not the group itself.
**How to avoid:**
- Use `pointer-events="all"` on interactive `<g>` groups to ensure unfilled areas respond
- Use `touch-action: manipulation` on the SVG container to disable double-tap zoom and reduce tap delay
- Use `event.target.closest('[data-region]')` to find the logical region, not the raw target element
- Add `cursor: pointer` to interactive elements for visual affordance
**Warning signs:** Taps work on desktop but not on iPad; taps only register on filled areas, not transparent gaps

### Pitfall 2: SVG ViewBox and Scaling Issues on iPad
**What goes wrong:** SVG renders at wrong size, is cropped, or doesn't fill the screen properly.
**Why it happens:** Missing or incorrect `viewBox` attribute. Safari is particularly sensitive to SVG sizing.
**How to avoid:**
- Always set `viewBox="0 0 [width] [height]"` on the root `<svg>` element
- Use `preserveAspectRatio="xMidYMid meet"` to center and contain the SVG
- Size the SVG container with CSS `width: 100%; height: auto` (or vice versa)
- Test on actual iPad resolution (2048x2732 for iPad Pro, 2160x1620 for iPad 10th gen)
**Warning signs:** SVG looks correct on desktop but is cut off, stretched, or tiny on iPad

### Pitfall 3: vtracer Output Too Complex / Too Many Paths
**What goes wrong:** Traced SVG has thousands of paths, is megabytes in size, and renders slowly.
**Why it happens:** Default vtracer settings trace every color variation in a high-resolution raster image.
**How to avoid:**
- Use `filter_speckle=10` or higher to remove tiny noise paths
- Use `color_precision=4` (instead of default 6) to reduce color layers
- Use `layer_difference=32` (instead of default 16) to merge similar colors
- Pre-process source images: reduce resolution to ~1024px, increase contrast, simplify backgrounds
- For Phase 1's simple silhouette, consider `colormode='binary'` for clean outlines
**Warning signs:** Output SVG file is >500KB; browser lag when displaying; hundreds of `<path>` elements

### Pitfall 4: Sparkle Animation Jank on iPad
**What goes wrong:** Sparkle particles stutter, jump, or cause the whole page to lag.
**Why it happens:** Creating too many DOM elements, forcing layout recalculation, or using JavaScript animation instead of CSS.
**How to avoid:**
- Use CSS `@keyframes` for all animation (GPU-accelerated on iPad)
- Use `transform` and `opacity` properties only (these are compositor-friendly)
- Limit sparkle particles to 6-8 per tap
- Remove sparkle elements from DOM after animation completes (`setTimeout` + `element.remove()`)
- Never animate `left`, `top`, `width`, `height` -- these trigger layout
**Warning signs:** Visible stuttering after several taps; memory usage climbing over time

### Pitfall 5: Overscroll Bounce Breaking the App Feel
**What goes wrong:** The entire page bounces when a child touches the edge, feeling like a website not an app.
**Why it happens:** iOS Safari's default rubber-band scrolling behavior.
**How to avoid:**
- Set `html, body { overflow: hidden; height: 100%; position: fixed; width: 100%; }`
- Use viewport meta: `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">`
- Add `overscroll-behavior: none` on body
- Add `touch-action: manipulation` on the main container
**Warning signs:** Content bounces when swiping up/down; address bar shows/hides during interaction

### Pitfall 6: Hash Routing Conflicts with SVG Fragment IDs
**What goes wrong:** SVG internal references like `url(#watercolor)` for filters break because the browser interprets `#watercolor` as a route hash.
**Why it happens:** Hash-based routing uses the URL fragment, which SVG also uses for internal references.
**How to avoid:**
- SVG `url()` references within inline SVG work fine because they resolve relative to the document, not the URL hash
- The hash router only reads `window.location.hash` which starts with `#/` -- SVG references like `url(#filterid)` are unaffected
- If issues arise, use `url(#filterid)` in SVG attributes (not CSS) to avoid any URL resolution ambiguity
**Warning signs:** SVG filters or gradients stop working when navigating between views

## Code Examples

### Complete HTML Shell for iPad Web App
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1,
        maximum-scale=1, user-scalable=no, viewport-fit=cover">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>Mermaid Create & Play</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <!-- Navigation bar - always visible -->
  <nav id="nav-bar">
    <a href="#/home" class="nav-icon" data-view="home" aria-label="Home">
      <!-- inline SVG home icon -->
    </a>
    <a href="#/dressup" class="nav-icon" data-view="dressup" aria-label="Dress Up">
      <!-- inline SVG dress-up icon -->
    </a>
    <a href="#/coloring" class="nav-icon" data-view="coloring" aria-label="Coloring">
      <!-- inline SVG coloring icon -->
    </a>
  </nav>

  <!-- View container - swapped by router -->
  <main id="app"></main>

  <script type="module" src="js/app.js"></script>
</body>
</html>
```

### CSS Foundation for iPad Full-Screen App
```css
/* Source: Apple viewport docs + iOS Safari best practices */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent; /* remove iOS tap highlight */
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: fixed;
  overscroll-behavior: none;
  touch-action: manipulation;
  font-family: -apple-system, sans-serif;
  background: #e8f4f8; /* soft ocean blue */
}

#app {
  width: 100%;
  height: calc(100% - 80px); /* minus nav bar */
  overflow: hidden;
}

/* Navigation */
#nav-bar {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 10px;
  height: 80px;
  background: rgba(255, 255, 255, 0.8);
}

.nav-icon {
  width: 60px;
  height: 60px;
  min-width: 60px;
  min-height: 60px;  /* FOUN-01: 60pt minimum */
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  text-decoration: none;
  touch-action: manipulation;
}

.nav-icon.active {
  background: rgba(100, 200, 255, 0.3);
}

/* SVG interaction */
[data-region] {
  cursor: pointer;
  touch-action: manipulation;
}

[data-region]:active {
  opacity: 0.8;
}
```

### vtracer Pipeline Script
```python
# Source: vtracer PyPI docs (v0.6.12)
import vtracer
from pathlib import Path
from PIL import Image


def trace_to_svg(
    input_path: str | Path,
    output_path: str | Path,
    *,
    simplify: bool = True,
) -> Path:
    """Convert a raster image to SVG using vtracer.

    For Phase 1 proof-of-concept, uses aggressive simplification
    to produce clean, small SVGs suitable for interactive regions.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Pre-process: resize to manageable dimensions
    img = Image.open(input_path)
    max_dim = 1024
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Save preprocessed image to temp
    temp_path = output_path.with_suffix('.preprocessed.png')
    img.save(temp_path)

    # Trace with settings tuned for clean interactive SVG
    params = dict(
        colormode='color',
        hierarchical='stacked',
        mode='spline',
        filter_speckle=10,       # remove small noise
        color_precision=4,        # fewer color layers
        layer_difference=32,      # merge similar colors
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3,         # fewer decimal places = smaller file
    )

    if simplify:
        # For Phase 1 silhouette, binary mode produces cleanest output
        params['colormode'] = 'binary'
        params['filter_speckle'] = 20

    vtracer.convert_image_to_svg_py(
        str(temp_path),
        str(output_path),
        **params,
    )

    temp_path.unlink()  # clean up
    return output_path
```

### Playwright iPad E2E Test
```python
# Source: Playwright Python docs + device emulation
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure iPad emulation for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1024, "height": 1366},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": (
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        ),
    }


def test_mermaid_svg_visible(page: Page):
    """FOUN-02: App loads and displays SVG mermaid."""
    page.goto("http://localhost:8000")
    svg = page.locator("#mermaid-svg")
    expect(svg).to_be_visible()


def test_tap_triggers_feedback(page: Page):
    """FOUN-04: Tapping SVG region shows visual feedback."""
    page.goto("http://localhost:8000/#/dressup")
    region = page.locator("[data-region='tail']")
    region.tap()
    sparkle = page.locator(".sparkle")
    expect(sparkle.first).to_be_visible()


def test_tap_targets_minimum_size(page: Page):
    """FOUN-01: All interactive elements are 60pt+ tap targets."""
    page.goto("http://localhost:8000")
    regions = page.locator("[data-region]")
    for i in range(regions.count()):
        box = regions.nth(i).bounding_box()
        assert box["width"] >= 60, f"Region {i} width {box['width']} < 60pt"
        assert box["height"] >= 60, f"Region {i} height {box['height']} < 60pt"


def test_navigation_between_views(page: Page):
    """NAVG-01 + NAVG-02: Navigate between home, dressup, coloring."""
    page.goto("http://localhost:8000")

    # Home shows two activity buttons
    expect(page.locator("[data-view='dressup']")).to_be_visible()
    expect(page.locator("[data-view='coloring']")).to_be_visible()

    # Navigate to dress-up
    page.locator("[data-view='dressup']").tap()
    expect(page).to_have_url("http://localhost:8000/#/dressup")

    # Navigate to coloring
    page.locator("[data-view='coloring']").tap()
    expect(page).to_have_url("http://localhost:8000/#/coloring")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Potrace (B&W only tracing) | vtracer (full-color, O(n)) | 2020+ | Can trace colored watercolor art directly instead of requiring preprocessing to B&W |
| FastClick library for 300ms delay | `touch-action: manipulation` CSS | 2016+ (iOS 9.3) | No library needed; CSS-only solution eliminates tap delay |
| jQuery + plugin for events | Vanilla JS + pointer events | 2018+ | `pointerdown`/`pointerup` unify mouse+touch; `closest()` replaces jQuery traversal |
| External SVG via `<img>` or `<object>` | Inline SVG in HTML | Always for interaction | Inline SVG is required for DOM event handling on individual elements |
| Canvas-based particle effects | CSS @keyframes on SVG elements | 2018+ | GPU-accelerated, no JS animation loop needed, simpler code |
| Server-side routing (Express/Flask templates) | Client-side hash routing | Always available | Zero server config; purely frontend navigation |

**Deprecated/outdated:**
- **FastClick library:** No longer needed. `touch-action: manipulation` handles the 300ms delay.
- **jQuery for DOM manipulation:** Vanilla JS `querySelector`, `closest()`, `addEventListener` cover all needs.
- **Potrace for colored images:** Only handles B&W. Use vtracer for colored artwork.

## Open Questions

1. **Which AI image tool produces art that traces best to SVG?**
   - What we know: DALL-E, Midjourney, Claude can all generate watercolor mermaid art. Recraft can generate SVG directly but quality is unknown for this use case.
   - What's unclear: Which tool's output has clean enough edges and limited enough color palette to trace well with vtracer.
   - Recommendation: Try 2-3 tools early in Wave 1, trace results, compare SVG quality. This is explicitly a "try and pick" decision per CONTEXT.md.

2. **Will SVG filters (feTurbulence) perform well on iPad Safari?**
   - What we know: SVG filters are supported in Safari. Complex filters with multiple stages can be slow.
   - What's unclear: Whether the watercolor filter stack causes rendering lag on iPad hardware.
   - Recommendation: Test the filter on a real iPad early. Have a fallback plan: apply watercolor texture at the raster level (before tracing) instead of as a live SVG filter. This may actually produce better results anyway since the texture becomes part of the traced paths.

3. **What is the ideal SVG structure for tappable mermaid regions?**
   - What we know: `<g>` groups with `data-region` attributes and invisible hit-area `<rect>` elements work well.
   - What's unclear: Whether post-vtracer SVG output can be automatically segmented into regions, or if manual SVG editing is needed.
   - Recommendation: Plan for manual SVG editing in Phase 1 (it's a single proof-of-concept asset). Automate in Phase 2 if the pattern is established.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8+ with pytest-playwright 0.6+ |
| Config file | none -- see Wave 0 |
| Quick run command | `uv run pytest tests/ -x --timeout=30` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUN-01 | All tap targets >= 60pt | e2e | `uv run pytest tests/test_e2e.py::test_tap_targets_minimum_size -x` | -- Wave 0 |
| FOUN-02 | App works in iPad Safari with touch | e2e | `uv run pytest tests/test_e2e.py::test_mermaid_svg_visible -x` | -- Wave 0 |
| FOUN-03 | Consistent watercolor art style | manual-only | Visual inspection of rendered SVG on iPad | N/A (manual) |
| FOUN-04 | Instant visual feedback on interaction | e2e | `uv run pytest tests/test_e2e.py::test_tap_triggers_feedback -x` | -- Wave 0 |
| NAVG-01 | Home screen has dress-up and coloring buttons | e2e | `uv run pytest tests/test_e2e.py::test_navigation_between_views -x` | -- Wave 0 |
| NAVG-02 | Switch activities from any screen | e2e | `uv run pytest tests/test_e2e.py::test_navigation_between_views -x` | -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x --timeout=30`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `pyproject.toml` -- project setup with dependencies
- [ ] `tests/conftest.py` -- shared fixtures (FastAPI test server, Playwright browser context with iPad settings)
- [ ] `tests/test_app.py` -- FastAPI static file serving tests
- [ ] `tests/test_pipeline.py` -- vtracer SVG tracing pipeline tests
- [ ] `tests/test_e2e.py` -- Playwright iPad emulation E2E tests
- [ ] Framework install: `uv add --dev pytest playwright pytest-playwright httpx && uv run playwright install webkit`

## Sources

### Primary (HIGH confidence)
- [FastAPI StaticFiles docs](https://fastapi.tiangolo.com/reference/staticfiles/) - Static file serving with html=True
- [MDN pointer-events SVG](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/pointer-events) - SVG pointer event attribute values
- [MDN touch-action](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action) - CSS touch-action property and Safari support
- [MDN feTurbulence](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feTurbulence) - SVG filter turbulence primitive
- [vtracer PyPI](https://pypi.org/project/vtracer/) - Python API for raster-to-SVG (v0.6.12)
- [Playwright Python emulation](https://playwright.dev/python/docs/emulation) - Device emulation including iPad profiles
- [Apple Safari event handling](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/HandlingEvents/HandlingEvents.html) - Touch event model in Safari

### Secondary (MEDIUM confidence)
- [Smashing Magazine SVG pointer-events](https://www.smashingmagazine.com/2018/05/svg-interaction-pointer-events-property/) - Comprehensive SVG interaction patterns
- [Codrops feTurbulence](https://tympanus.net/codrops/2019/02/19/svg-filter-effects-creating-texture-with-feturbulence/) - SVG filter texture creation techniques
- [Go Make Things SVG event delegation](https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/) - Vanilla JS event delegation pattern for SVG
- [BugFactory FastAPI static files](https://bugfactory.io/articles/how-to-serve-a-directory-of-static-files-with-fastapi/) - SPA serving with html=True pattern
- [dev.to vanilla JS SPA](https://dev.to/dcodeyt/building-a-single-page-app-without-frameworks-hl9) - Hash and History API routing patterns
- [vtracer GitHub](https://github.com/visioncortex/vtracer) - Full-color tracing vs Potrace comparison

### Tertiary (LOW confidence)
- [CodePen watercolor SVG filter](https://codepen.io/cassie-codes/pen/GRJzgLL) - Watercolor painting effect implementation (could not fetch full code)
- SVG filter performance on iPad Safari -- no authoritative benchmarks found; needs real-device testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI, vtracer, Playwright all have solid official docs; versions verified on PyPI
- Architecture: HIGH - Hash routing, inline SVG, pointer events are well-documented browser standards
- Art pipeline: MEDIUM - vtracer is solid, but AI-image-to-clean-SVG quality is an unknown that needs prototyping
- Pitfalls: MEDIUM-HIGH - iPad Safari quirks are well-documented; sparkle performance is based on general CSS animation knowledge
- Watercolor filters: MEDIUM - The filter primitives are standard, but performance on iPad and visual quality need real testing

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable technologies, no fast-moving dependencies)
