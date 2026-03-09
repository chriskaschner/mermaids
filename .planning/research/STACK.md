# Technology Stack

**Project:** Mermaid Create & Play
**Researched:** 2026-03-09
**Verification note:** Web search and Context7 tools were unavailable during this research session. All version numbers and recommendations are based on training data (cutoff ~May 2025). Versions should be verified before `uv add` / `npm install`. Confidence levels are adjusted downward accordingly.

## Recommended Stack

### Backend: Python + FastAPI

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | 3.12+ | Runtime | User preference. 3.12 has good perf improvements. | HIGH |
| FastAPI | ~0.115+ | API + static serving | Lightweight, async, serves static files trivially. Perfect for weekend-project scale -- no Django overhead. | MEDIUM (verify version) |
| Uvicorn | ~0.32+ | ASGI server | Standard FastAPI server. Single `uvicorn main:app` command. | MEDIUM (verify version) |
| Jinja2 | ~3.1+ | HTML templating | FastAPI integrates natively. Renders initial page with asset manifests. Avoids need for JS build tooling entirely. | MEDIUM (verify version) |
| Pillow | ~11.0+ | Image processing | Convert AI-generated art to print-ready formats. Generate coloring page outlines from watercolor originals (edge detection). Resize/optimize for web. | MEDIUM (verify version) |

**Why FastAPI over alternatives:**
- Django: Too heavy for a weekend project with no database, no auth, no admin. Overkill.
- Flask: Viable but FastAPI is more modern, has better async support, and native type hints.
- Plain file server: Not enough -- we need at least one API endpoint for print/save functionality.

### Frontend: Vanilla JS + SVG-First + Canvas for Export

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Vanilla JavaScript | ES2022+ | App logic | No framework needed. This is a single-page creative tool, not a data-driven SPA. React/Vue add build complexity for zero benefit here. | HIGH |
| SVG (inline DOM) | Native | Dress-up, scene builder, coloring fill | SVG elements are individually selectable, draggable, and scalable without pixelation. Each mermaid part is a discrete SVG element. Recoloring is trivial (change `fill` attribute). Region-based coloring works by tapping SVG paths. Memory-efficient on iPad. | HIGH |
| HTML5 Canvas API | Native | Export/print only | Canvas is used only for final rendering: export SVG composition to PNG for saving/printing via `canvas.toDataURL()`. Not used for interactive manipulation. | HIGH |
| CSS Custom Properties | Native | Theming / colors | Swap color palettes for mermaid parts without JS. Keep styling declarative. | HIGH |
| Pointer Events API | Native | Touch/mouse input | Use `pointerdown`/`pointermove`/`pointerup` instead of separate touch/mouse handlers. Safari supports pointer events since iOS 13. Eliminates duplicate event bugs. | HIGH |

**The SVG-first decision is critical.** Here is why SVG over Canvas for the interactive layer:

1. **iPad Safari memory.** Canvas backing stores consume GPU memory. Multiple large canvases or one very large canvas can trigger Safari's silent tab-kill. SVG uses the DOM, which Safari manages more gracefully.
2. **Dress-up is object manipulation.** Each mermaid part (tail, hair, crown) is a discrete thing you tap and swap. SVG elements ARE discrete things. Canvas requires an object model library (Fabric.js, Konva) to fake this -- SVG gives it natively.
3. **Recoloring for free.** Change `element.style.fill = '#9B59B6'` and the tail is purple. In Canvas, you'd need to redraw.
4. **Coloring pages with SVG regions.** Pre-segmented SVG paths let the user tap a region to fill it. No flood-fill algorithm, no anti-aliased edge bleed, no performance concerns. Instant, pixel-perfect.
5. **Print quality.** SVG renders at any resolution. Export to Canvas at 300 DPI for print -- sharp at any size.
6. **Compact state.** Saving an SVG composition is a small JSON object (which elements, which colors, which positions). No pixel data.

**When Canvas IS still needed:**
- Exporting compositions as PNG for gallery thumbnails and printing
- A potential "free brush" painting mode for coloring (stretch goal, not MVP)

**Why vanilla over frameworks:**

1. **Weekend project scope.** Every minute spent on `npm create vite@latest`, configuring TypeScript, setting up component trees, is a minute not spent on the fun part (making mermaids work).
2. **No state complexity.** The app state is: which mermaid parts are selected, what colors are applied. This fits in a plain JS object. No need for Redux, Zustand, or even React state.
3. **No build step.** Serve `.html`, `.js`, `.css` files directly from FastAPI's `StaticFiles`. Edit, refresh, done.
4. **Touch events are simpler in vanilla.** No synthetic event system to fight with. Pointer events directly on SVG elements.
5. **iPad Safari compatibility.** Fewer layers = fewer Safari-specific bugs.

### Canvas Library: None Required (SVG-first approach)

With SVG as the primary interactive rendering approach, a canvas abstraction library (Fabric.js, Konva.js) is **not needed** for the interactive layer. The browser's SVG DOM provides:

- Hit detection (native SVG element click/pointer events)
- Z-ordering (SVG element order = visual order)
- Drag-and-drop (pointer events + transform attributes)
- Scaling/rotation (SVG `transform` attribute)
- Selection (CSS styling on SVG elements)

A small utility module (~100 lines) handles SVG drag-and-drop with touch support. This is simpler and more reliable than configuring a canvas library.

**For the export step** (SVG -> PNG for saving/printing), use the browser-native approach:
```javascript
// Render SVG to Canvas for export
const svgData = new XMLSerializer().serializeToString(svgElement);
const img = new Image();
img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgData);
img.onload = () => {
  ctx.drawImage(img, 0, 0);
  const png = canvas.toDataURL('image/png');
};
```

**If SVG proves insufficient** (performance with many elements, complex compositing needs), Fabric.js ~6.x is the fallback. But start without it.

### Print Support

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| CSS @media print | Native | Print styling | Hide UI, show only the coloring page at full size. Zero dependencies. | HIGH |
| window.print() | Native | Trigger print | One button. Works on iPad Safari (opens AirPrint via share sheet). | HIGH |
| SVG -> Canvas export | Native | High-res rendering | Render SVG at print resolution (300 DPI) to Canvas, then export PNG/PDF. | HIGH |
| Pillow (server, stretch) | ~11.0+ | PDF generation | Server-side PDF with proper page margins. Stretch goal. | MEDIUM |

**Print strategy:**
1. Primary: CSS print stylesheet hides everything except the coloring page, rendered at full page size. `window.print()` triggers iPad's AirPrint dialog.
2. For coloring outlines: serve high-res SVG directly. SVG prints crisply at any DPI.
3. Fallback: "Save to Photos" button exports as PNG. User prints from Photos app.
4. Server-side (stretch): Pillow generates PDF with proper margins for letter-size paper.

### Art Asset Pipeline

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| AI image generation | -- | Create watercolor mermaid art | Per project spec. Use whatever tool produces best watercolor style (DALL-E 3, Midjourney, Stable Diffusion). | HIGH |
| SVG tracing / manual creation | -- | Convert art to SVG | AI generates reference images; trace to clean SVG paths for dress-up parts and coloring regions. Tools: Vectorizer.ai, Adobe Illustrator auto-trace, Inkscape. | MEDIUM |
| Pillow (server) | ~11.0+ | Process raster assets | Background removal, outline generation, resize, optimize. | MEDIUM (verify version) |
| TinyPNG/Squoosh | -- | Compress raster fallbacks | If any PNG assets are needed (backgrounds), compress before serving. | HIGH |
| SVGOMG | -- | Optimize SVGs | Clean up SVG markup, remove unnecessary metadata, reduce file size. | HIGH |

**Asset format strategy:**
- **Dress-up parts (tail, hair, crown, etc.):** SVG preferred. Each part is an SVG group with named paths for recoloring. PNG fallback if SVG tracing proves too difficult for watercolor style.
- **Scene backgrounds:** PNG or JPEG. Static, non-interactive. Single image per scene.
- **Coloring page outlines:** SVG with pre-segmented regions (each fillable area is a named `<path>`). This enables tap-to-fill coloring without flood-fill algorithms.
- **All assets pre-generated.** No runtime AI generation. Generate a library of ~20-40 parts, 5-8 backgrounds, 10-15 coloring pages before launch.

**Asset pipeline decision: SVG vs PNG for dress-up parts.**
This is the riskiest asset decision. AI generators produce raster images, not SVGs. Converting watercolor art to clean SVGs requires either:
- Auto-tracing (Vectorizer.ai, potrace) -- may lose watercolor character
- Manual tracing in Inkscape/Illustrator -- time-consuming but high quality
- Hybrid: use SVG for shapes/structure, embed raster watercolor textures as SVG `<image>` fills

**Recommendation:** Start with the hybrid approach. SVG paths define the shapes (tail outline, hair outline). Use CSS/SVG pattern fills with the watercolor texture. This gives SVG's interactivity benefits while preserving the watercolor look.

### Storage: Local-Only

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| localStorage | Native | Save creations | Persist SVG state (element IDs + transforms + colors) as JSON. ~5MB limit is plenty for JSON state. | HIGH |
| IndexedDB | Native | Save images (stretch) | If localStorage isn't enough for saved PNG thumbnails, IndexedDB handles binary blobs. | HIGH |

**Why no database:**
- Single user (one 6-year-old).
- No accounts, no sharing, no server-side persistence needed.
- localStorage is synchronous, simple, and sufficient.
- If the iPad clears Safari data, she makes new mermaids. That is fine.

### Dev Tooling

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| uv | latest | Python package management | User preference. Fast, replaces pip/venv. | HIGH |
| pytest | ~8.x | Backend testing | Test image processing endpoints, API routes. | MEDIUM (verify version) |
| Playwright | ~1.49+ | E2E / visual testing | Test touch interactions on SVG elements. Can emulate iPad viewport and WebKit engine. Catches Safari-specific rendering bugs. | MEDIUM (verify version) |
| eslint | -- | JS linting | Optional but catches bugs in vanilla JS (no TypeScript safety net). | MEDIUM |

**Why Playwright over alternatives:**
- Cypress: Does not support Safari/WebKit. Playwright does via WebKit engine.
- Puppeteer: Chrome only. Cannot test Safari behavior.
- Manual testing: Works for a weekend project, but Playwright lets you automate "tap here, drag there, check SVG state" which is exactly what this app needs.

## Full Stack Summary

```
[iPad Safari]
    |
    | HTTPS (or local network)
    |
[FastAPI + Uvicorn]
    |--- Static files (HTML, JS, CSS, SVG assets)
    |--- Jinja2 templates (index.html)
    |--- /api/export-pdf (stretch: server-side PDF generation)
    |
[Browser]
    |--- Vanilla JS app logic
    |--- SVG DOM (dress-up, coloring, scene builder interactions)
    |--- Canvas (export only: SVG -> PNG for save/print)
    |--- localStorage (save/load JSON state)
    |--- CSS print stylesheet (print coloring pages)
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend | FastAPI | Django | No ORM, no admin, no auth needed. Django is 10x the complexity for this project. |
| Backend | FastAPI | Flask | Flask works but FastAPI has better async, type hints, and auto-docs. Marginal difference for this project. |
| Frontend | Vanilla JS | React | Build tooling overhead, synthetic events complicate touch handling, component model adds complexity for zero benefit in a single-page creative tool. |
| Frontend | Vanilla JS | Svelte | Closest to vanilla in output, but still requires build step. Not worth it for this scope. |
| Frontend | Vanilla JS | htmx | Interesting for form-heavy apps, but creative canvas interactions are entirely client-side. htmx adds nothing here. |
| Rendering | SVG DOM | Fabric.js | Fabric.js adds a dependency and forces Canvas-based rendering. SVG gives hit detection, z-ordering, and recoloring for free. For a dress-up app (discrete objects, not pixel painting), SVG is the simpler and more performant choice on iPad. |
| Rendering | SVG DOM | Konva.js | Same reasoning as Fabric.js. Canvas library overhead for a problem SVG solves natively. |
| Rendering | SVG DOM | Raw Canvas | Hundreds of lines of hit detection, z-ordering, touch mapping code. SVG DOM provides all of this via standard DOM APIs. |
| Rendering | SVG DOM | PixiJS | Game engine. Designed for 60fps animation loops. Massive overhead for a creative tool with no animation requirements. |
| Storage | localStorage | SQLite | No server-side persistence needed. Single user, no auth. localStorage is simpler. |
| Storage | localStorage | Firebase | Cloud service for a single-user weekend project with no accounts. Absurd overhead. |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| TypeScript | Build step overhead. Vanilla JS is fine for a project this size. Add TS if the project grows past weekend scope. |
| React / Vue / Angular | Framework overhead for zero benefit. See detailed rationale above. |
| Webpack / Vite / Rollup | No build step needed. Serve files directly. |
| Tailwind CSS | Build step. Hand-written CSS for ~5 screens is faster than configuring Tailwind. |
| Fabric.js / Konva.js | Canvas abstraction libraries add complexity. SVG DOM handles dress-up and coloring interactions natively. Only add if SVG approach hits a wall during prototyping. |
| Docker | Weekend project running locally or on a simple server. Docker adds deployment complexity. |
| PostgreSQL / MySQL | No relational data. No server-side persistence needed. |
| Redis | No caching layer needed. Static assets + localStorage. |
| WebSockets | No real-time features. No multiplayer. HTTP requests suffice. |
| Service Workers / PWA | Nice-to-have but not MVP. Add later if she wants offline access. |
| npm / yarn / pnpm | No JS build tooling. No JS dependencies to install (all native or vendored). |

## Installation

```bash
# Backend setup with uv
uv init mermaids
cd mermaids
uv add fastapi uvicorn jinja2 pillow python-multipart

# Dev dependencies
uv add --dev pytest playwright pytest-playwright httpx

# Install Playwright browsers (need WebKit for Safari testing)
uv run playwright install webkit

# Frontend: No build step. No JS package manager.
# All frontend code is vanilla JS + SVG + CSS served as static files.
# No npm install, no node_modules, no bundler.
```

## iPad Safari Specific Notes

| Concern | Solution | Confidence |
|---------|----------|------------|
| Touch events | Use Pointer Events API (pointerdown/pointermove/pointerup). Safari supports since iOS 13. Handles touch and mouse uniformly. | HIGH |
| 300ms tap delay | Add `<meta name="viewport" content="width=device-width">` -- modern Safari eliminates delay with this. Also add `touch-action: manipulation` on interactive elements. | HIGH |
| Pinch-to-zoom conflicts | Set `touch-action: none` on the SVG/canvas interaction area. Prevents browser zoom while interacting. | HIGH |
| Bounce scroll | `overflow: hidden` on body + `overscroll-behavior: none`. Prevents rubber-band scrolling over interaction area. | HIGH |
| Swipe-back navigation | SPA architecture (no page navigation). `touch-action: none` on main area claims gestures. | HIGH |
| Save to Photos | Render SVG to Canvas, `canvas.toDataURL()` -> create download link. Or use Web Share API (`navigator.share()`). | MEDIUM |
| Print | `window.print()` opens AirPrint dialog via share sheet. CSS `@media print` hides UI. | HIGH |
| SVG rendering quality | SVG renders natively in Safari at full Retina resolution. No pixel density workaround needed (unlike Canvas). | HIGH |
| Maximum canvas size (export) | iPad Safari limits canvas to ~16 megapixels (~4096x4096). Keep export canvas under this. SVG interaction is not subject to this limit. | MEDIUM |
| Audio (stretch) | Web Audio API requires user gesture to start. Attach `audioCtx.resume()` to first pointer event. | HIGH |
| 100vh bug | Use `100dvh` (dynamic viewport height) instead of `100vh` to account for Safari toolbar. | HIGH |
| CSS hover sticky | Use `@media (hover: hover)` for hover styles. Use `:active` for touch feedback. | HIGH |

## Sources

- FastAPI documentation (fastapi.tiangolo.com) -- training data, verify current version
- SVG specification and MDN SVG docs -- training data, HIGH confidence (stable spec)
- Apple Safari Web Content Guide -- training data for iPad-specific behaviors
- MDN Web Docs -- Pointer Events API, SVG DOM, Canvas export APIs
- Pillow documentation (pillow.readthedocs.io) -- training data, verify current version

**Confidence note:** All version numbers are from training data with a May 2025 cutoff. Run `uv add fastapi` (without pinning) to get the latest, then pin in `pyproject.toml`. The SVG and Canvas APIs are stable web standards unlikely to have changed. The primary verification needed is for Python library versions.
