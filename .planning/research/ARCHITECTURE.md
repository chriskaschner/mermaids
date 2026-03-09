# Architecture Patterns

**Domain:** Kids creative activity web app (dress-up, coloring, scene builder)
**Researched:** 2026-03-09

## Recommended Architecture

Simple client-heavy architecture. The server is just a file server with one or two utility endpoints. All interactive logic lives in the browser. SVG DOM is the primary rendering layer; Canvas is used only for PNG export.

```
+--------------------------------------------------+
|                iPad Safari Browser                 |
|                                                    |
|  +----------------------------------------------+ |
|  |          App Shell (HTML/CSS, Tab Nav)        | |
|  |  +----------+ +----------+ +----------+      | |
|  |  | Dress-Up | | Coloring | |  Scene   |      | |
|  |  |   Mode   | |   Mode   | | Builder  |      | |
|  |  +----+-----+ +----+-----+ +----+-----+      | |
|  |       |             |            |            | |
|  |  +----v-------------v------------v-----+      | |
|  |  |         SVG Composition Layer       |      | |
|  |  |  (inline SVG, DOM manipulation)     |      | |
|  |  |  - Mermaid parts as SVG groups      |      | |
|  |  |  - Touch via Pointer Events API     |      | |
|  |  |  - Recoloring via fill attributes   |      | |
|  |  +----+--------------------------------+      | |
|  |       |                                       | |
|  |  +----v-----------+  +-------------------+    | |
|  |  | State Manager  |  | Asset Loader      |    | |
|  |  | (plain JS obj) |  | (preload SVGs)    |    | |
|  |  +----+-----------+  +-------------------+    | |
|  |       |                                       | |
|  |  +----v-----------+  +-------------------+    | |
|  |  | localStorage   |  | Canvas (export    |    | |
|  |  | (save/load)    |  |  only: SVG->PNG)  |    | |
|  |  +----------------+  +-------------------+    | |
|  +----------------------------------------------+ |
+-------------------------+------------------------+
                          |
                    HTTP (static)
                          |
+-------------------------v------------------------+
|              FastAPI Server                        |
|                                                    |
|  /                  -> index.html (Jinja2)         |
|  /static/           -> JS, CSS, SVG/image assets   |
|  /api/export-pdf    -> Pillow PDF generation       |
|                        (stretch goal)              |
+--------------------------------------------------+
```

### Why This Shape

1. **Client-heavy, server-light.** All creative interaction must feel instant (a 6-year-old will not wait for network round-trips). SVG manipulation, drag-and-drop, coloring -- all happens in the browser with zero server calls.

2. **SVG-first, not Canvas-first.** This is a dress-up app (discrete objects), not a painting app (pixel manipulation). SVG elements are the natural representation: each mermaid part is a DOM element you can tap, drag, recolor, and serialize. Canvas abstraction libraries (Fabric.js, Konva.js) recreate what SVG already provides natively.

3. **No database.** For a single-user weekend project, localStorage is the database. Saved creations are JSON objects (which SVG elements, which colors, which positions). This eliminates an entire category of complexity.

4. **Python backend because the user prefers it.** FastAPI serves static files and optionally generates print-ready PDFs. It does not participate in any interactive rendering.

5. **Pre-generated assets, not runtime-generated.** Mermaid parts, scene backgrounds, and coloring page outlines are AI-generated ahead of time and served as static SVG/image files.

## Component Boundaries

| Component | Responsibility | Communicates With | Technology |
|-----------|---------------|-------------------|------------|
| **App Shell** | Navigation between activities (tabs), layout, responsive sizing | All activity modules | HTML/CSS, vanilla JS |
| **Dress-Up Module** | Swap mermaid parts, drag accessories, select colors | SVG Layer, Asset Loader, State Manager | JS module manipulating SVG DOM |
| **Coloring Module** | Tap SVG regions to fill with color, palette selection | SVG Layer, State Manager | JS module, SVG path fill attributes |
| **Scene Builder Module** | Place dressed mermaid into background, add decorations | SVG Layer, Asset Loader, State Manager | JS module manipulating SVG DOM |
| **SVG Composition Layer** | The inline SVG element containing all visual content | All activity modules (consumer) | Inline SVG in HTML |
| **State Manager** | Current mode, selected parts, undo history, gallery data | localStorage, all modules | Plain JS object |
| **Asset Loader** | Preload and cache SVG/image assets | SVG Layer (injects loaded content) | JS fetch + DOM |
| **Export Controller** | Render SVG to Canvas for PNG export, trigger print | SVG Layer, hidden Canvas element | XMLSerializer + Canvas API |
| **Print Controller** | CSS print stylesheet, PDF download (stretch) | Export Controller, FastAPI endpoint | CSS @media print, fetch |

### Component Boundary Rules

- **Activity modules never talk to each other directly.** The dress-up module produces a "customized mermaid" (SVG state). The scene builder consumes it. Communication goes through saved state, not direct coupling.
- **All visual rendering goes through SVG.** Activity modules modify SVG element attributes (visibility, fill, transform). They never draw pixels directly.
- **Canvas is export-only.** A hidden `<canvas>` element exists solely for `SVG -> PNG` conversion when saving or printing. It is never displayed to the user.
- **The backend never knows about SVG state.** It receives finished PNGs and JSON state blobs. It does not interpret or manipulate them (except for optional PDF generation).

## Detailed Component Design

### SVG Composition Layer

The central visual element is a single inline `<svg>` element in the HTML, sized to fill the interaction area. All mermaid parts, coloring pages, and scene elements live inside this SVG as groups (`<g>`) and paths (`<path>`).

**SVG layer structure:**
```xml
<svg id="stage" viewBox="0 0 1024 1024">
  <!-- Background layer (scene image or white) -->
  <g id="layer-background">
    <image href="/static/scenes/coral-reef.jpg" width="1024" height="1024" />
  </g>

  <!-- Mermaid body layer -->
  <g id="layer-body">
    <use href="#body-01" />
  </g>

  <!-- Mermaid tail layer -->
  <g id="layer-tail">
    <use href="#tail-flowing" fill="#9B59B6" />
  </g>

  <!-- Mermaid hair layer -->
  <g id="layer-hair">
    <use href="#hair-braided" fill="#C0392B" />
  </g>

  <!-- Accessories layer (draggable items) -->
  <g id="layer-accessories">
    <use href="#crown-gold" transform="translate(150,30) scale(1.0)" />
    <use href="#necklace-pearl" transform="translate(160,120) scale(0.8)" />
  </g>

  <!-- Scene decorations layer -->
  <g id="layer-decorations">
    <use href="#fish-01" transform="translate(600,200)" />
    <use href="#coral-01" transform="translate(100,700)" />
  </g>

  <!-- Coloring page layer (hidden except in coloring mode) -->
  <g id="layer-coloring" display="none">
    <path id="region-tail" d="..." fill="#FFFFFF" stroke="#333" stroke-width="3" />
    <path id="region-body" d="..." fill="#FFFFFF" stroke="#333" stroke-width="3" />
    <!-- ... more regions -->
  </g>
</svg>

<!-- Asset definitions (hidden, referenced by <use>) -->
<svg id="asset-defs" style="display:none">
  <defs>
    <g id="body-01">...</g>
    <g id="tail-flowing">...</g>
    <g id="hair-braided">...</g>
    <g id="crown-gold">...</g>
    <!-- ... all dress-up parts as SVG groups -->
  </defs>
</svg>
```

**Why SVG `<use>` with `<defs>`:**
- Assets defined once, instantiated via `<use href="#id">`. Swapping a tail means changing the `href` attribute.
- Fill color on `<use>` cascades to child paths (CSS inheritance). Recoloring is one attribute change.
- `<defs>` content is not rendered. No GPU cost for unused assets.
- All assets can be loaded in a single SVG sprite file or injected from individual SVG files.

**Touch handling on SVG:**
```javascript
// Pointer events work on SVG elements just like HTML elements
accessoryElement.addEventListener('pointerdown', startDrag);
document.addEventListener('pointermove', onDrag);
document.addEventListener('pointerup', endDrag);

function startDrag(e) {
  e.preventDefault(); // Prevent scroll/zoom
  dragging = e.target.closest('[data-draggable]');
  dragOffset = getSVGPoint(e) - getElementPosition(dragging);
}

function onDrag(e) {
  if (!dragging) return;
  const point = getSVGPoint(e);
  dragging.setAttribute('transform',
    `translate(${point.x - dragOffset.x}, ${point.y - dragOffset.y})`
  );
}
```

### Dress-Up Module

**State model:**
```json
{
  "body": "body-01",
  "tail": { "id": "tail-flowing", "color": "#9B59B6" },
  "hair": { "id": "hair-braided", "color": "#C0392B" },
  "accessories": [
    { "id": "crown-gold", "x": 150, "y": 30, "scale": 1.0 },
    { "id": "necklace-pearl", "x": 160, "y": 120, "scale": 0.8 }
  ]
}
```

**Interaction flow:**
1. Panel on side/bottom shows category tabs (tail, hair, accessories)
2. Tap an option -> JS changes the `href` attribute on the corresponding `<use>` element
3. Tap a color swatch -> JS changes the `fill` attribute on the `<use>` element
4. Accessories are draggable via pointer events + SVG `transform` attribute
5. State is a plain JSON object. Save = `JSON.stringify(state)` -> `localStorage.setItem()`.

### Coloring Module

**SVG region-based approach (recommended):**

Each coloring page is an SVG with pre-segmented regions as `<path>` elements. Initial fill is white (or transparent). User taps a region -> `path.style.fill = selectedColor`. Instant, no pixel manipulation.

```javascript
coloringPaths.forEach(path => {
  path.addEventListener('pointerdown', () => {
    path.style.fill = currentColor;
    pushUndo();
  });
});
```

This eliminates the need for:
- Flood-fill algorithms (complex, performance-sensitive)
- Anti-aliased edge handling (the SVG paths define exact boundaries)
- Web Workers for pixel processing
- Pixel-level undo (just reset the fill attribute)

**Color palette:** 12-16 large (60x60pt minimum) color swatches. Curated for watercolor aesthetic: soft pink, lavender, seafoam, coral, sky blue, pale gold, ocean teal, sunset orange, sand beige, pearl white, midnight purple, forest green. No free color picker.

### Scene Builder Module

Reuses dress-up mechanics. Background is an `<image>` element in the SVG. Mermaid (from dress-up state) is placed as a group. Decorations (fish, coral, treasure) are additional draggable `<use>` elements.

### Export Controller (SVG -> PNG)

```javascript
function exportToPNG(svgElement, scale = 2) {
  const svgData = new XMLSerializer().serializeToString(svgElement);
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  const img = new Image();
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = svgElement.viewBox.baseVal.width * scale;
    canvas.height = svgElement.viewBox.baseVal.height * scale;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    URL.revokeObjectURL(url);

    // Now canvas.toDataURL() or canvas.toBlob() for save/print
    const png = canvas.toDataURL('image/png');
    return png;
  };
  img.src = url;
}
```

**For print (300 DPI on letter paper):** Use scale = 3-4 (3072-4096px on long edge). Keep under iPad Safari's ~16 megapixel canvas limit.

### Data Flow

**Dress-Up Flow:**
1. User taps a tail option in the parts panel
2. Dress-Up Module updates state: `{ tail: { id: "tail-sparkle", color: "#3498DB" } }`
3. JS sets `document.querySelector('#layer-tail use').href.baseVal = '#tail-sparkle'`
4. JS sets `document.querySelector('#layer-tail use').style.fill = '#3498DB'`
5. SVG re-renders instantly (browser-native, no JS rendering loop)

**Coloring Flow:**
1. User selects "Coral Reef" coloring page
2. Coloring Module loads the SVG paths for that page into the coloring layer
3. User taps a color swatch -> `currentColor = '#E74C3C'`
4. User taps a region -> `region.style.fill = '#E74C3C'`
5. State Manager records fill changes for undo

**Print Flow:**
1. User taps "Print" on a coloring page
2. CSS `@media print` hides all UI, shows only the coloring SVG at full page size
3. `window.print()` triggers iPad's AirPrint via share sheet
4. Alternative: Export Controller renders SVG to high-res PNG, creates download link

**Save/Load Flow:**
1. User taps "Save"
2. State Manager serializes current state as JSON (~1-5KB)
3. Export Controller generates thumbnail PNG (~50KB)
4. JSON + base64 thumbnail stored in localStorage under gallery key
5. Gallery view reads localStorage, renders thumbnails
6. Tap thumbnail -> load JSON state -> restore SVG element attributes

## Patterns to Follow

### Pattern 1: Single SVG, Multiple Modes
**What:** One inline SVG element, reconfigured per activity mode by toggling layer visibility.
**When:** Always. Do not create multiple SVG elements for each activity.
**Why:** Consistent coordinate space. One place for pointer event handling. Easy to composite across activities (dress-up mermaid appears in scene builder).
**Example:**
```javascript
function switchMode(mode) {
  // Hide all activity-specific layers
  document.querySelectorAll('[data-activity-layer]').forEach(
    g => g.setAttribute('display', 'none')
  );

  if (mode === 'dressup') {
    show('layer-body', 'layer-tail', 'layer-hair', 'layer-accessories');
    showPanel('parts-panel');
  } else if (mode === 'coloring') {
    show('layer-coloring');
    showPanel('color-palette');
  } else if (mode === 'scene') {
    show('layer-background', 'layer-body', 'layer-tail', 'layer-hair',
         'layer-accessories', 'layer-decorations');
    showPanel('scene-panel');
  }
}
```

### Pattern 2: Asset Preloading with Visible Progress
**What:** Load all SVG asset definitions on app start, before any interaction.
**When:** App initialization.
**Why:** A 6-year-old will not wait for assets to load after tapping. Everything must be instant.
**Example:**
```javascript
async function preloadAssets(manifestUrl) {
  const manifest = await fetch(manifestUrl).then(r => r.json());
  const svgDefs = document.getElementById('asset-defs').querySelector('defs');

  await Promise.all(manifest.assets.map(async (asset) => {
    const resp = await fetch(asset.url);
    const svgText = await resp.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgText, 'image/svg+xml');
    const group = doc.querySelector('svg > g') || doc.querySelector('svg');
    group.id = asset.id;
    svgDefs.appendChild(document.importNode(group, true));
  }));
}
```

### Pattern 3: Undo as State Stack
**What:** Push current state JSON to an array on each meaningful action. Pop to undo.
**When:** After each drag-end, color fill, or part swap.
**Why:** Simple, reliable. SVG state is just attributes on DOM elements -- serialization is trivial.
**Example:**
```javascript
const undoStack = [];
const MAX_UNDO = 20;

function pushUndo() {
  undoStack.push(JSON.parse(JSON.stringify(currentState)));
  if (undoStack.length > MAX_UNDO) undoStack.shift();
}

function undo() {
  if (undoStack.length === 0) return;
  currentState = undoStack.pop();
  applyState(currentState); // Set SVG attributes from state
}
```

### Pattern 4: Oversized Touch Targets
**What:** All interactive elements are minimum 60x60pt. Invisible hit areas extend beyond visible artwork.
**When:** Always. Non-negotiable for a 6-year-old user.
**Example:**
```javascript
// For small SVG accessories, add an invisible hit area
function addHitArea(svgGroup, padding = 20) {
  const bbox = svgGroup.getBBox();
  const hitRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  hitRect.setAttribute('x', bbox.x - padding);
  hitRect.setAttribute('y', bbox.y - padding);
  hitRect.setAttribute('width', bbox.width + padding * 2);
  hitRect.setAttribute('height', bbox.height + padding * 2);
  hitRect.setAttribute('fill', 'transparent');
  hitRect.setAttribute('data-draggable', 'true');
  svgGroup.insertBefore(hitRect, svgGroup.firstChild);
}
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Canvas for Interactive Layer
**What:** Using HTML5 Canvas (with or without Fabric.js/Konva.js) as the primary interaction layer.
**Why bad:** Canvas has no built-in object model. Every interactive element needs manual hit detection. iPad Safari has strict canvas memory limits (~16 megapixels). Canvas libraries add bundle size and API surface area for capabilities SVG provides natively.
**Instead:** SVG DOM for all interaction. Canvas only for PNG export.

### Anti-Pattern 2: Framework-Driven SVG
**What:** Wrapping SVG manipulation in React/Vue components, using virtual DOM to manage SVG state.
**Why bad:** Virtual DOM diffing on SVG elements adds latency. Framework event system adds a layer between pointer events and SVG. Debugging requires understanding both framework and SVG lifecycles.
**Instead:** Direct DOM manipulation. `element.setAttribute()` is the entire rendering API.

### Anti-Pattern 3: Lazy-Loading Assets
**What:** Loading SVG assets on-demand when the user taps a mermaid part.
**Why bad:** Network latency means a visible delay between tap and appearance. A 6-year-old interprets this as "broken."
**Instead:** Preload everything on splash screen. Show a fun loading animation (swimming mermaid, rising bubbles).

### Anti-Pattern 4: Complex State Management
**What:** Using a state management library (Redux, MobX, Zustand) for SVG state.
**Why bad:** SVG state is just attributes on DOM elements. Duplicating it in a state store creates sync bugs. The "state" is: which `href` is set, which `fill` is set, which `transform` is set. A plain JS object mirrors this trivially.
**Instead:** Plain JS state object. Serialize with `JSON.stringify()`. Restore by setting attributes.

### Anti-Pattern 5: SPA Router
**What:** Using hash-based or history-based routing between activities.
**Why bad:** URL changes enable Safari's swipe-back gesture, which can navigate away from the app and lose unsaved work. A 6-year-old will accidentally trigger this.
**Instead:** Tab-based navigation within a single page. JS toggles visibility. No URL changes after initial load.

## File Structure

```
mermaids/
  main.py                  # FastAPI app, routes, optional PDF endpoint
  static/
    css/
      app.css              # Main styles + CSS custom properties for theming
      print.css            # Print-only styles (@media print)
    js/
      app.js               # App shell, mode switching, initialization
      dressup.js           # Dress-up mode logic (part swapping, dragging)
      coloring.js          # Coloring mode logic (region fill, palette)
      scene.js             # Scene builder logic
      gallery.js           # Save/load/gallery logic
      assets.js            # SVG asset preloader
      drag.js              # SVG drag-and-drop utility (~100 lines)
      export.js            # SVG -> Canvas -> PNG export
    assets/
      sprites.svg          # All dress-up parts as SVG defs (or individual files)
      parts/               # Individual SVG files if not using sprite
        tails/
        hair/
        crowns/
        accessories/
      backgrounds/          # Scene backgrounds (PNG/JPEG)
      coloring/             # Coloring page SVGs with pre-segmented regions
      ui/                   # UI icons (SVG)
  templates/
    index.html             # Jinja2 template, single page, inline SVG stage
  tests/
    test_main.py           # FastAPI endpoint tests
    test_e2e.py            # Playwright E2E tests (WebKit)
  pyproject.toml           # uv project config
```

## Scalability Considerations

This is a single-user weekend project. Scalability is not a concern. But for completeness:

| Concern | At 1 user (target) | At 100 users (unlikely) | At 10K users (absurd) |
|---------|---------------------|-------------------------|------------------------|
| Server load | FastAPI serves static files. Negligible. | Still negligible. | Put assets on CDN. |
| Storage | localStorage per device. | Same. Each device independent. | Still same. No server persistence. |
| Asset delivery | ~2-5MB total SVG+images. One-time load. | Same assets for everyone. | CDN with cache headers. |
| SVG perf | Depends on iPad model. ~20 SVG elements is trivial. | N/A (client-side). | N/A (client-side). |

## Sources

- SVG specification and MDN SVG documentation (stable web standard)
- Pointer Events API (MDN, W3C spec) -- stable, well-supported
- Apple Human Interface Guidelines (touch targets, viewport behavior)
- FastAPI documentation (static file serving, Jinja2 templates)
- HTML5 Canvas API for export (MDN) -- stable
