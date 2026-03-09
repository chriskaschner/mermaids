# Phase 3: Coloring - Research

**Researched:** 2026-03-09
**Domain:** SVG coloring pages, tap-to-fill interaction, thumbnail gallery, color palette reuse, undo system
**Confidence:** HIGH

## Summary

Phase 3 adds a coloring page activity to the app. The existing codebase provides nearly everything needed: the same COLORS palette (10 swatches), the same undo pattern (command stack), the same CSS styling for swatches and buttons, and the same SVG-based rendering pipeline. The coloring feature is structurally simpler than dress-up because there is no variant swapping -- only tap-a-region-to-fill-it.

Each coloring page is a standalone SVG file with closed-path regions that start with `fill="white"` (or a very light base) and a visible `stroke` outline. Tapping a region changes its `fill` to the currently selected color. The coloring screen has two states: (1) a thumbnail gallery showing 4-6 page previews, and (2) the active coloring view with the selected page full-screen plus the color palette and undo button below it. The gallery-to-page transition is simple DOM replacement -- no animation library needed.

The main implementation work is: (a) creating 4-6 coloring page SVGs with well-defined tappable regions, (b) building the gallery thumbnail view with page selection, (c) wiring tap-to-fill with the shared color palette, and (d) adding undo support using the same command stack pattern from dress-up. No new libraries are needed. No backend changes are required.

**Primary recommendation:** Create a `coloring.js` module mirroring the structure of `dressup.js`. Each coloring page SVG uses `data-region` attributes on fillable `<path>` groups. Tap handling reuses the `pointerdown` + `event.target.closest("[data-region]")` pattern from `touch.js`. Color palette and undo are extracted or duplicated from dress-up.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| COLR-01 | User can view 4-6 mermaid-themed coloring pages | Gallery view with thumbnail previews; each page is an inline SVG; thumbnails are scaled-down versions of the same SVGs |
| COLR-02 | User can tap a region on a coloring page to fill it with the selected color | SVG regions marked with `data-region`; `pointerdown` event delegation; `setAttribute("fill", color)` on the target region's fill-bearing elements |
| COLR-03 | User can select colors from the same 8-12 swatch palette | Reuse the `COLORS` array from `dressup.js` (10 colors); render identical `.color-swatch` buttons |
| COLR-04 | User can undo last color fill with a single tap | Command stack pattern identical to dress-up; each fill action captures previous fill for undo |

</phase_requirements>

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Backend server, static file serving | Project decision; already installed |
| uvicorn | 0.34+ | ASGI server | Already installed |

### Supporting (already installed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8+ | Python test framework | All backend and pipeline tests |
| playwright | 1.49+ | Browser automation | E2E tests with iPad emulation |
| pytest-playwright | 0.6+ | Pytest Playwright integration | Test runner integration |
| httpx | 0.28+ | Async HTTP client | FastAPI test client |

### No new dependencies needed

Phase 3 requires zero new libraries. Tap-to-fill coloring uses the same `setAttribute("fill", color)` pattern, the same `pointerdown` event delegation, and the same command stack undo as Phase 2. The gallery thumbnail grid uses standard CSS flexbox/grid.

## Architecture Patterns

### Recommended File Structure Changes
```
frontend/
  assets/
    svg/
      mermaid.svg                    # EXISTING: dress-up mermaid
      coloring/
        page-1-ocean.svg             # NEW: coloring page SVGs (4-6 files)
        page-2-castle.svg
        page-3-seahorse.svg
        page-4-coral.svg
        page-5-treasure.svg
        page-6-friends.svg
  js/
    app.js                           # MODIFIED: renderColoring() builds gallery + coloring UI
    coloring.js                      # NEW: coloring state, tap-to-fill, undo, page selection
    dressup.js                       # EXISTING: unchanged
    touch.js                         # EXISTING: unchanged
    sparkle.js                       # EXISTING: unchanged
  css/
    style.css                        # MODIFIED: add coloring gallery grid and coloring view styles
```

### Pattern 1: Coloring Page SVG Structure

**What:** Each coloring page is an SVG with closed-path regions. Regions start with a light fill (white or very light gray) and a visible stroke outline. Each fillable region has a `data-region` attribute for event delegation.

**When to use:** For every coloring page SVG (COLR-01, COLR-02).

**Why this structure:** The `data-region` pattern is already proven in the dress-up SVG. Using closed paths with explicit strokes ensures the coloring book "outline" look. Starting with `fill="white"` rather than `fill="none"` means regions are visible and tappable (elements with `fill="none"` have no hit area unless `pointer-events="all"` is set).

**Example:**
```xml
<!-- coloring/page-1-ocean.svg -->
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 600 800"
     id="coloring-page">

  <!-- Mermaid body region -->
  <g data-region="body" pointer-events="all">
    <path d="M250,200 Q240,280 235,350 L365,350 Q360,280 350,200 Z"
          fill="white" stroke="#555" stroke-width="2" />
  </g>

  <!-- Tail region -->
  <g data-region="tail" pointer-events="all">
    <path d="M235,350 Q220,420 200,500 Q250,540 300,520 Q350,540 400,500
             Q380,420 365,350 Z"
          fill="white" stroke="#555" stroke-width="2" />
  </g>

  <!-- Hair region -->
  <g data-region="hair" pointer-events="all">
    <path d="M220,100 Q200,50 250,30 Q300,20 350,50 Q380,100 370,180
             L230,180 Q210,140 220,100 Z"
          fill="white" stroke="#555" stroke-width="2" />
  </g>

  <!-- Background elements (seaweed, bubbles, etc.) -->
  <g data-region="seaweed-1" pointer-events="all">
    <path d="M50,400 Q60,350 55,300 Q65,350 70,400 Q60,380 50,400 Z"
          fill="white" stroke="#555" stroke-width="1.5" />
  </g>

  <!-- Non-fillable outlines (always black) -->
  <g pointer-events="none">
    <circle cx="270" cy="160" r="8" fill="none" stroke="#333" stroke-width="2" />
    <circle cx="330" cy="160" r="8" fill="none" stroke="#333" stroke-width="2" />
    <path d="M280,185 Q300,200 320,185" fill="none" stroke="#333" stroke-width="2" />
  </g>
</svg>
```

### Pattern 2: Gallery Thumbnail View

**What:** The coloring screen initially shows a grid of 4-6 thumbnails. Each thumbnail is a small rendered version of the coloring page SVG, wrapped in a tappable button. Tapping a thumbnail loads that page into the full coloring view.

**When to use:** For COLR-01 (viewing coloring page choices).

**Layout:**
```
+------------------------------------------+
|                                          |
|   [Page 1]   [Page 2]   [Page 3]        |
|                                          |
|   [Page 4]   [Page 5]   [Page 6]        |
|                                          |
+------------------------------------------+
| [home] [dressup] [coloring]              |  <-- Nav bar (existing)
+------------------------------------------+
```

**Example:**
```javascript
// Coloring page metadata
const COLORING_PAGES = [
  { id: "page-1-ocean", label: "Ocean Mermaid", file: "/assets/svg/coloring/page-1-ocean.svg" },
  { id: "page-2-castle", label: "Mermaid Castle", file: "/assets/svg/coloring/page-2-castle.svg" },
  { id: "page-3-seahorse", label: "Seahorse Friend", file: "/assets/svg/coloring/page-3-seahorse.svg" },
  { id: "page-4-coral", label: "Coral Reef", file: "/assets/svg/coloring/page-4-coral.svg" },
];

function renderGallery(container) {
  container.innerHTML = `
    <div class="coloring-gallery">
      ${COLORING_PAGES.map(page => `
        <button class="gallery-thumb" data-page="${page.id}" aria-label="${page.label}">
          <img src="${page.file}" alt="${page.label}" />
        </button>
      `).join("")}
    </div>
  `;
}
```

**Important note on thumbnails:** Using `<img src="...svg">` for thumbnails is fine for display purposes since the thumbnails are not interactive. The full-size active coloring page must be inlined as SVG (not `<img>`) so that individual path elements are accessible to JavaScript for tap-to-fill.

### Pattern 3: Tap-to-Fill with Event Delegation

**What:** A single `pointerdown` listener on the coloring page SVG root. Uses `event.target.closest("[data-region]")` to find the tapped region. Changes fill on all fill-bearing children of that region to the currently selected color.

**When to use:** For COLR-02 (tap to fill a region).

**Example:**
```javascript
function initColoringInteraction(svgRoot) {
  svgRoot.addEventListener("pointerdown", (event) => {
    const region = event.target.closest("[data-region]");
    if (!region) return;

    const color = getSelectedColor();
    if (!color) return;

    // Capture previous fills for undo
    const elements = getFillableElements(region);
    const previousFills = elements.map(el => ({
      element: el,
      fill: el.getAttribute("fill"),
    }));

    // Apply new color
    elements.forEach(el => el.setAttribute("fill", color));

    // Push undo
    pushUndo(() => {
      previousFills.forEach(({ element, fill }) => {
        element.setAttribute("fill", fill);
      });
    });
  });
}

function getFillableElements(regionGroup) {
  return Array.from(
    regionGroup.querySelectorAll("path, circle, ellipse, rect")
  ).filter(el => {
    const fill = el.getAttribute("fill");
    return fill && fill !== "none";
  });
}
```

### Pattern 4: Color Palette and Undo Reuse

**What:** The same 10-color COLORS array from dress-up, the same `.color-swatch` button rendering, and the same command stack undo pattern. The coloring view has its own undo stack (separate from dress-up) and its own selected-color state.

**When to use:** For COLR-03 (color palette) and COLR-04 (undo).

**Options for reuse:**

**Option A (recommended): Duplicate the palette and undo in coloring.js.** The COLORS array is 10 items. The undo stack is ~15 lines of code. Duplicating is simpler than creating a shared module, avoids coupling the two activities, and allows the coloring palette to diverge in the future (e.g., adding an eraser "color" that resets to white).

**Option B: Extract shared module.** Create a `shared.js` module exporting COLORS, pushUndo, undo. Both `dressup.js` and `coloring.js` import from it. Cleaner but adds a third JS module and coupling.

**Recommendation:** Option A. The duplication is trivial (~20 lines), and the two activities have different state lifecycles. Coloring undo tracks per-region fills; dress-up undo tracks part swaps and per-variant recoloring. Mixing them in a shared stack would be a bug factory.

### Pattern 5: Back Button (Gallery <-> Coloring Page)

**What:** When a user selects a coloring page, the view changes from the gallery to the full coloring view. A "back to gallery" button lets the child return to pick a different page. The current page's coloring state is preserved if they return to it.

**When to use:** Navigation within the coloring activity.

**Example:**
```javascript
const coloringState = {};  // { "page-1-ocean": { fills: {...} }, ... }

function openPage(pageId) {
  // Fetch and inline the SVG
  // Restore any saved fills from coloringState[pageId]
  // Show coloring UI (palette + undo + back button)
}

function backToGallery() {
  // Save current fills to coloringState[currentPageId]
  // Re-render the gallery
}
```

### Anti-Patterns to Avoid

- **Using `<img>` tags for the active coloring page:** `<img>` renders SVG as a flat image -- JavaScript cannot access internal paths. The active page MUST be inlined as `<svg>` in the DOM.
- **Using `fill="none"` for unfilled regions:** Elements with `fill="none"` have no hit area by default. Use `fill="white"` so regions are both visible and tappable without needing `pointer-events="all"` on every path.
- **Single global undo stack across dress-up and coloring:** The two activities have completely different state models. A shared stack would let undoing in coloring revert a dress-up action if the user switches activities.
- **Loading all 6 SVGs at page load:** Fetch coloring page SVGs on demand when the user selects one. Thumbnails can use `<img>` tags which the browser handles efficiently.
- **Complex flood-fill algorithm:** This is not a pixel-based coloring app. Each fillable region is a pre-defined SVG path. Clicking a region fills the entire path -- no flood-fill algorithm needed.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Region detection on tap | Custom hit-testing / point-in-polygon | `event.target.closest("[data-region]")` | Browser handles SVG hit-testing natively; `closest()` traverses to the attributed group |
| Flood fill / paint bucket | Canvas-based pixel flood fill | Pre-defined SVG path regions with `setAttribute("fill")` | SVG paths ARE the regions; fill is a single attribute change, not pixel manipulation |
| Thumbnail rendering | Canvas screenshot / server-side rendering | `<img src="page.svg">` in thumbnail grid | Browser renders SVG natively in `<img>` tags; no JS needed for preview |
| Color palette | Custom color picker / HSL wheel | Fixed swatch array + CSS circle buttons | A 6-year-old needs 10 big colorful circles, not a color picker |
| State persistence across page visits | localStorage / IndexedDB | In-memory JS object `coloringState[pageId]` | App is ephemeral (no save feature in v1); in-memory state survives within a session |
| Undo system | Event sourcing / memento pattern | Simple array push/pop with closures | Same pattern proven in dress-up; ~15 lines of code |

**Key insight:** Coloring pages are the simplest SVG interaction pattern in this app. Each region is a closed path. Tapping it changes one attribute. The entire coloring engine is ~50 lines of JavaScript plus the SVG assets.

## Common Pitfalls

### Pitfall 1: SVG Regions Too Small for Child Fingers

**What goes wrong:** Small decorative elements (bubbles, stars, tiny fish) are impossible for a 6-year-old to tap accurately.
**Why it happens:** Coloring page art has fine details that look great on paper but are too small as touch targets.
**How to avoid:** Design coloring page regions to be large (minimum 60pt equivalent). Small decorative elements should either be grouped into larger regions or be non-interactive (pre-filled outline-only details). Test with the 60pt minimum from FOUN-01.
**Warning signs:** Child taps repeatedly but nothing happens; wrong region fills instead of intended one.

### Pitfall 2: Stroke Outlines Disappearing After Fill

**What goes wrong:** After filling a region with a dark color, the stroke outline between adjacent regions becomes invisible.
**Why it happens:** The stroke is rendered before the fill of the adjacent region, or the stroke color is too similar to the fill.
**How to avoid:** Use a consistent dark stroke (`#333` or `#555`) with `stroke-width="2"` or greater. SVG renders strokes on top of fills by default, so the outline remains visible. If needed, use `paint-order: stroke` to ensure strokes render after fills.
**Warning signs:** Regions visually merge when filled with similar colors.

### Pitfall 3: Thumbnail `<img>` vs Inline SVG Confusion

**What goes wrong:** Thumbnails work fine but tapping a thumbnail opens an `<img>` version of the SVG, and tap-to-fill does nothing.
**Why it happens:** Developer forgets to fetch and inline the SVG as DOM elements when transitioning from gallery to coloring view.
**How to avoid:** Gallery thumbnails use `<img src="page.svg">`. The active coloring page must fetch the SVG text via `fetch()` and insert it with `innerHTML`, just like `renderDressUp()` does with `mermaid.svg`.
**Warning signs:** SVG displays correctly but click/tap events have no effect.

### Pitfall 4: Undo Stack Not Reset Between Pages

**What goes wrong:** User colors page 1, switches to page 2, taps undo -- and it tries to revert a fill on page 1 (which is no longer in the DOM).
**Why it happens:** Undo closures reference DOM elements from the previous page.
**How to avoid:** Clear the undo stack when switching coloring pages. Each page gets a fresh undo stack. Save/restore fills separately from the undo stack.
**Warning signs:** Undo does nothing or throws a JS error after switching pages.

### Pitfall 5: `pointerdown` on Stroke-Only Elements

**What goes wrong:** Tapping exactly on a stroke line (the outline between two regions) does not fill any region.
**Why it happens:** The stroke belongs to one path element, but the user's intent is ambiguous -- they could mean either adjacent region.
**How to avoid:** Set `pointer-events="all"` on region `<g>` groups, and ensure the `<g>` has a fill-bearing child element. Using `fill="white"` on region paths ensures the entire area (not just the stroke) is tappable.
**Warning signs:** Some taps register and fill regions; others seem to do nothing.

### Pitfall 6: Coloring Page SVGs Not Found (404)

**What goes wrong:** Navigating to the coloring view shows broken thumbnails or "could not load" errors.
**Why it happens:** SVG files placed in wrong directory, or FastAPI static file mount does not serve the subdirectory.
**How to avoid:** The existing `StaticFiles(directory=_frontend_dir, html=True)` mount serves ALL files under `frontend/`, including subdirectories. Place coloring SVGs in `frontend/assets/svg/coloring/` and reference them as `/assets/svg/coloring/page-1-ocean.svg`. Verify with a direct browser request before wiring up JavaScript.
**Warning signs:** 404 errors in the browser console; broken image icons in the gallery.

## Code Examples

### Complete Coloring Module Structure

```javascript
// coloring.js -- coloring page state, tap-to-fill, color palette, undo
// Source: mirrors patterns from dressup.js and touch.js in this codebase

// Same 10-color palette as dress-up
export const COLORS = [
  "#7ec8c8", "#c4a7d7", "#ff69b4", "#ffd700", "#87ceeb",
  "#98fb98", "#ff6347", "#dda0dd", "#ffa07a", "#40e0d0",
];

// Coloring page definitions
export const COLORING_PAGES = [
  { id: "page-1-ocean", label: "Ocean Mermaid", file: "/assets/svg/coloring/page-1-ocean.svg" },
  { id: "page-2-castle", label: "Mermaid Castle", file: "/assets/svg/coloring/page-2-castle.svg" },
  { id: "page-3-seahorse", label: "Seahorse Friend", file: "/assets/svg/coloring/page-3-seahorse.svg" },
  { id: "page-4-coral", label: "Coral Reef", file: "/assets/svg/coloring/page-4-coral.svg" },
];

// State
const state = {
  selectedColor: COLORS[2],  // default to hot pink
  currentPageId: null,
};

const undoStack = [];
const MAX_UNDO = 30;

// Saved fills per page (survives page switching within session)
const savedFills = {};  // { "page-1-ocean": { "body": "#ff69b4", ... }, ... }

// -- Core operations --

export function fillRegion(regionGroup, color) {
  const elements = getFillableElements(regionGroup);
  if (elements.length === 0) return;

  const previousFills = elements.map(el => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));

  elements.forEach(el => el.setAttribute("fill", color));

  pushUndo(() => {
    previousFills.forEach(({ element, fill }) => {
      element.setAttribute("fill", fill);
    });
  });
}

export function undo() {
  const cmd = undoStack.pop();
  if (cmd) cmd.undo();
}

export function setSelectedColor(color) {
  state.selectedColor = color;
}

export function getSelectedColor() {
  return state.selectedColor;
}

// -- Helpers --

function getFillableElements(regionGroup) {
  return Array.from(
    regionGroup.querySelectorAll("path, circle, ellipse, rect")
  ).filter(el => {
    const fill = el.getAttribute("fill");
    return fill && fill !== "none";
  });
}

function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) undoStack.shift();
}

export function resetColoringState() {
  undoStack.length = 0;
  state.currentPageId = null;
  state.selectedColor = COLORS[2];
}

export { state };
```

### Coloring View HTML Structure (generated by renderColoring in app.js)

```html
<!-- Gallery view (initial state) -->
<div class="coloring-gallery">
  <button class="gallery-thumb" data-page="page-1-ocean" aria-label="Ocean Mermaid">
    <img src="/assets/svg/coloring/page-1-ocean.svg" alt="Ocean Mermaid" />
  </button>
  <button class="gallery-thumb" data-page="page-2-castle" aria-label="Mermaid Castle">
    <img src="/assets/svg/coloring/page-2-castle.svg" alt="Mermaid Castle" />
  </button>
  <!-- ... more pages ... -->
</div>

<!-- Active coloring view (after selecting a page) -->
<div class="coloring-view">
  <div class="coloring-page-container" id="coloring-container">
    <!-- Inlined SVG goes here via fetch + innerHTML -->
  </div>
  <div class="coloring-panel">
    <div class="coloring-toolbar">
      <button class="back-btn" aria-label="Back to pages">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M15,4 L7,12 L15,20" fill="none" stroke="#888"
                stroke-width="2.5" stroke-linecap="round" />
        </svg>
      </button>
      <button class="undo-btn" aria-label="Undo">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M7,12 L3,8 L7,4 M3,8 L15,8 Q20,8 20,14 Q20,20 15,20 L10,20"
                fill="none" stroke="#888" stroke-width="2.5" stroke-linecap="round" />
        </svg>
      </button>
    </div>
    <div class="options-row" id="color-swatches">
      <!-- Color swatches rendered dynamically -->
    </div>
  </div>
</div>
```

### Coloring View CSS

```css
/* Coloring gallery */
.coloring-gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  height: 100%;
  align-content: center;
}

.gallery-thumb {
  aspect-ratio: 3 / 4;
  border: 3px solid #ddd;
  border-radius: 16px;
  background: white;
  padding: 8px;
  cursor: pointer;
  touch-action: manipulation;
  min-height: 120px;
}

.gallery-thumb:active {
  transform: scale(0.95);
  border-color: #5b8fa8;
}

.gallery-thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Active coloring view */
.coloring-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.coloring-page-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
}

.coloring-page-container svg {
  max-width: 100%;
  max-height: 100%;
}

.coloring-panel {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.coloring-toolbar {
  display: flex;
  gap: 8px;
  padding: 4px 8px;
  justify-content: space-between;
}

.back-btn {
  width: 60px;
  height: 60px;
  min-width: 60px;
  min-height: 60px;
  border: 2px solid transparent;
  border-radius: 14px;
  background: rgba(200, 220, 240, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: manipulation;
  cursor: pointer;
}
```

### Wiring renderColoring in app.js

```javascript
// In app.js -- replace the placeholder renderColoring()
import { COLORING_PAGES, COLORS, initColoring, resetColoringState } from "./coloring.js";

async function renderColoring() {
  const el = appEl();
  // Show gallery of coloring pages
  el.innerHTML = `
    <div class="coloring-gallery">
      ${COLORING_PAGES.map(page => `
        <button class="gallery-thumb" data-page="${page.id}" aria-label="${page.label}">
          <img src="${page.file}" alt="${page.label}" />
        </button>
      `).join("")}
    </div>
  `;

  // Wire gallery thumbnail clicks
  el.querySelectorAll(".gallery-thumb").forEach(btn => {
    btn.addEventListener("click", () => {
      const pageId = btn.dataset.page;
      openColoringPage(pageId);
    });
  });
}

async function openColoringPage(pageId) {
  const page = COLORING_PAGES.find(p => p.id === pageId);
  if (!page) return;

  const el = appEl();
  el.innerHTML = '<div class="loading">Loading...</div>';

  try {
    const resp = await fetch(page.file);
    const svgText = await resp.text();

    el.innerHTML = `
      <div class="coloring-view">
        <div class="coloring-page-container" id="coloring-container">
          ${svgText}
        </div>
        <div class="coloring-panel">
          <div class="coloring-toolbar">
            <button class="back-btn" aria-label="Back to pages">
              <!-- back arrow SVG -->
            </button>
            <button class="undo-btn" aria-label="Undo">
              <!-- undo arrow SVG -->
            </button>
          </div>
          <div class="options-row" id="color-swatches"></div>
        </div>
      </div>
    `;

    initColoring(pageId);
  } catch (err) {
    el.innerHTML = '<div class="error">Could not load page.</div>';
  }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Canvas-based flood fill (pixel scanning) | Pre-defined SVG path regions with `setAttribute("fill")` | Always valid for SVG apps | No pixel manipulation; instant fill; resolution-independent |
| jQuery `.click()` with `.attr("style")` | Vanilla JS `addEventListener("pointerdown")` + `.setAttribute("fill")` | 2020+ (modern JS) | No jQuery dependency; pointer events handle both mouse and touch |
| Server-rendered page thumbnails | `<img src="file.svg">` for thumbnails | Always valid | Browser renders SVGs natively; no server processing needed |

**Deprecated/outdated:**
- **jQuery for SVG manipulation:** Vanilla JS `setAttribute()` and `querySelector()` are sufficient and lighter. No jQuery in this project.

## Open Questions

1. **Coloring Page Art Content**
   - What we know: We need 4-6 mermaid-themed coloring page SVGs. Each must have well-defined regions with `data-region` attributes, large enough for child touch targets.
   - What's unclear: Whether these will be hand-crafted SVGs (guaranteed structure) or AI-generated art traced with vtracer and then edited.
   - Recommendation: Hand-craft all coloring page SVGs. The structure requirements (closed paths, `data-region` attributes, minimum region sizes, consistent stroke widths) make hand-crafting faster than cleaning up traced AI art. Each page needs 8-15 fillable regions -- a manageable amount of SVG path work.

2. **Gallery Grid Layout (2 vs 3 columns)**
   - What we know: iPad portrait is 1024px wide. The gallery needs to show 4-6 thumbnails.
   - What's unclear: Whether 2 columns (2x3 grid) or 3 columns (3x2 grid) is better for thumb reach and visual appeal.
   - Recommendation: Use 3 columns for 6 pages or 2 columns for 4 pages. With 3 columns and 16px gap, each thumbnail is approximately 320px wide -- large and easy to tap.

3. **State Preservation When Switching Pages**
   - What we know: User might color page 1, go back to gallery, color page 2, then return to page 1.
   - What's unclear: Should page 1's colors be preserved?
   - Recommendation: Preserve fills in an in-memory state object keyed by page ID. When re-opening a page, restore saved fills. Do NOT persist to localStorage (out of scope for v1). Undo stack is reset on page switch (undo closures hold DOM references from the previous page, which are invalid after switching).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8+ with pytest-playwright 0.6+ |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/ -x` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COLR-01 | Coloring screen shows 4-6 thumbnails | e2e | `uv run pytest tests/test_coloring.py::TestColoringGallery::test_gallery_shows_thumbnails -x` | -- Wave 0 |
| COLR-01 | Tapping thumbnail opens coloring page | e2e | `uv run pytest tests/test_coloring.py::TestColoringGallery::test_thumbnail_opens_page -x` | -- Wave 0 |
| COLR-02 | Tapping region fills with selected color | e2e | `uv run pytest tests/test_coloring.py::TestColoringFill::test_tap_region_fills_color -x` | -- Wave 0 |
| COLR-03 | Color swatches available (8-12 colors) | e2e | `uv run pytest tests/test_coloring.py::TestColoringPalette::test_swatches_visible -x` | -- Wave 0 |
| COLR-03 | Tapping swatch changes selected color | e2e | `uv run pytest tests/test_coloring.py::TestColoringPalette::test_swatch_changes_selection -x` | -- Wave 0 |
| COLR-04 | Undo reverts last fill | e2e | `uv run pytest tests/test_coloring.py::TestColoringUndo::test_undo_reverts_fill -x` | -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_coloring.py` -- Playwright E2E tests for all COLR requirements
- [ ] Coloring page SVG assets (4-6 files in `frontend/assets/svg/coloring/`)
- [ ] `frontend/js/coloring.js` -- coloring module
- [ ] Existing `tests/test_e2e.py` may need updates if `renderColoring()` changes from placeholder to real implementation (currently tests that navigating to coloring view works, but assertions are minimal)

## Sources

### Primary (HIGH confidence)
- [MDN SVG Fills and Strokes](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorials/SVG_from_scratch/Fills_and_strokes) - Fill attribute behavior, fill vs none, stroke rendering order
- [MDN SVG color attribute](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/color) - SVG color and presentation attribute behavior
- [SVG Interactive Tutorial](https://svg-tutorial.com/svg/interaction/) - Click handlers on SVG elements, `setAttribute("fill")` pattern, cursor feedback
- Existing codebase: `frontend/js/dressup.js`, `frontend/js/touch.js` -- proven patterns for SVG tap-to-fill and event delegation in this project

### Secondary (MEDIUM confidence)
- [SVG Coloring Book (GitHub Gist)](https://gist.github.com/widged/4545199) - Click handler on SVG elements applies selected color's style; validates the `event.target` + `setAttribute` approach
- [SVG Coloring Book Plugin (CodePen)](https://codepen.io/MacEvelly/pen/YXyRVE) - jQuery-based coloring book with swatch selection and SVG region filling
- [Embedding External SVG for JS Manipulation](https://www.javaspring.net/blog/embedding-external-svg-in-html-for-javascript-manipulation/) - Inline SVG vs `<img>` tag for JavaScript access to SVG elements
- [Interactive SVG Map (freeCodeCamp)](https://www.freecodecamp.org/news/how-to-make-clickable-svg-map-html-css/) - Clickable SVG regions with event listeners

### Tertiary (LOW confidence)
- Gallery state preservation across page switches -- no authoritative source; implementation will follow the in-memory object pattern used by dress-up state, validated empirically

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Zero new dependencies; all browser-native SVG DOM APIs
- Architecture (tap-to-fill on SVG regions): HIGH - Identical pattern to existing dress-up recoloring; validated by multiple CodePen examples and MDN documentation
- Gallery thumbnail view: HIGH - Standard CSS grid + `<img>` tags; trivial implementation
- Color palette reuse: HIGH - Exact same COLORS array and `.color-swatch` button pattern from Phase 2
- Undo system: HIGH - Exact same command stack pattern from Phase 2; proven in dress-up
- Coloring page SVG art: MEDIUM - Structure is well-defined but hand-crafting 4-6 pages with proper region sizing is an art task that needs empirical validation for touch target sizing

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable browser APIs, no fast-moving dependencies)
