# Phase 2: Dress-Up - Research

**Researched:** 2026-03-09
**Domain:** SVG part-swapping, color recoloring, undo system, completion animation, vanilla JS state management
**Confidence:** HIGH

## Summary

Phase 2 builds the dress-up mechanic on top of the Phase 1 SVG foundation. The existing mermaid SVG (400x700 viewBox, three `data-region` groups: hair/body/tail, watercolor filter) must be restructured into a multi-variant system where each region (tail, hair, accessory) contains 3-4 visual variants, with only one visible at a time. Part swapping uses `display: none` / `display: inline` toggling on SVG `<g>` groups. Color recoloring uses `setAttribute("fill", color)` on the `<g>` group, which cascades to all child `<path>` and shape elements via SVG inheritance. The undo system uses a simple command stack (array of `{undo()}` objects). The celebration sparkle uses the existing `sparkle.js` system scaled up (more particles, wider spread) when all parts are selected.

The app is vanilla JS with no framework, no build step, served by FastAPI. The existing codebase uses ES modules (`type="module"`), pointer event delegation on SVG elements, and hash-based routing. Phase 2 adds a new JS module (`dressup.js`) for state management, part selection UI (bottom panel with thumbnail buttons), color palette, and undo button. All interactive elements must maintain 60pt+ tap targets for a 6-year-old.

**Primary recommendation:** Structure the mermaid SVG with all variants embedded in `<defs>`, instantiated via `<use>` elements. Swap parts by changing `<use href="#tail-2">` rather than showing/hiding groups. This keeps the SVG clean and makes adding new variants trivial.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DRSS-01 | User can view a base mermaid character on screen | Existing mermaid SVG from Phase 1 renders in dress-up view; restructure with variant system, default variant visible on load |
| DRSS-02 | User can swap between 3-4 tail options by tapping | SVG `<use>` element with `href` attribute pointing to tail variants defined in `<defs>`; bottom panel with tail thumbnail buttons; tap handler updates href |
| DRSS-03 | User can swap between 3-4 hair style options by tapping | Same `<use>` + `<defs>` pattern as DRSS-02; separate category in selection panel |
| DRSS-04 | User can add/swap crowns and accessories (3-4 options) | New accessory `<use>` element; accessories layer on top of base mermaid; "none" option allows removal |
| DRSS-05 | User can recolor mermaid parts by tapping color swatches (8-12 colors) | `setAttribute("fill", color)` on the active region's `<use>` element; fill cascades to children via SVG inheritance; color swatch palette with 60pt+ tap targets |
| DRSS-06 | User can undo last action with a single tap | Command stack pattern: each action pushes `{undo: fn}` to array; undo button pops and executes; no redo needed |
| DRSS-07 | Sparkle/bubble animation plays when all parts are selected | Track selected state for tail/hair/accessory; when all three have non-default selections, trigger enhanced sparkle using existing `sparkle.js` |

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

Phase 2 requires zero new libraries. All part-swapping, color-changing, undo, and animation are achieved with vanilla JS + SVG DOM APIs that already exist in the browser.

## Architecture Patterns

### Recommended File Structure Changes
```
frontend/
  assets/
    svg/
      mermaid.svg             # RESTRUCTURED: variants in <defs>, <use> for active parts
  js/
    app.js                    # MODIFIED: renderDressUp() builds full dress-up UI
    touch.js                  # EXISTING: pointer event delegation (may need minor updates)
    sparkle.js                # EXISTING: reused for completion celebration
    dressup.js                # NEW: dress-up state, part swapping, color, undo logic
  css/
    style.css                 # MODIFIED: add selection panel, color palette, undo button styles
```

### Pattern 1: SVG Variant System with `<defs>` + `<use>`

**What:** Define all part variants (3-4 tails, 3-4 hairs, 3-4 accessories) as `<g>` groups inside `<defs>`. Use `<use href="#variant-id">` elements in the main SVG to display the active variant for each category.

**When to use:** For DRSS-02, DRSS-03, DRSS-04 (part swapping).

**Why this over show/hide:** Swapping `href` on a single `<use>` element is one DOM operation. Show/hide requires finding the visible group, hiding it, then showing the new one -- three operations plus risk of multiple variants becoming visible simultaneously.

**Example:**
```xml
<!-- Inside mermaid.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 700" id="mermaid-svg">
  <defs>
    <filter id="watercolor">...</filter>

    <!-- Tail variants -->
    <g id="tail-1">
      <path d="M155,340 Q140,380..." fill="#7ec8c8" />
      <!-- scales, fin, etc. -->
    </g>
    <g id="tail-2">
      <path d="M160,340 Q145,385..." fill="#7ec8c8" />
      <!-- different tail shape -->
    </g>
    <g id="tail-3">...</g>

    <!-- Hair variants -->
    <g id="hair-1">...</g>
    <g id="hair-2">...</g>
    <g id="hair-3">...</g>

    <!-- Accessory variants -->
    <g id="acc-1"><!-- crown --></g>
    <g id="acc-2"><!-- flower --></g>
    <g id="acc-3"><!-- starfish --></g>
    <g id="acc-none"><!-- empty group, no accessory --></g>
  </defs>

  <g filter="url(#watercolor)">
    <!-- Active parts rendered via <use> -->
    <use id="active-tail" href="#tail-1" data-region="tail" pointer-events="all" />
    <use id="active-hair" href="#hair-1" data-region="hair" pointer-events="all" />

    <!-- Body (not swappable in v1, just one version) -->
    <g data-region="body" pointer-events="all">
      <path d="M155,140 Q145,170..." fill="#f5c8a8" />
      <!-- torso, arms, etc. -->
    </g>

    <!-- Accessory layer (on top) -->
    <use id="active-acc" href="#acc-none" data-region="accessory" pointer-events="all" />
  </g>

  <!-- Face details (outside watercolor filter) -->
  <ellipse cx="185" cy="75" rx="5" ry="6" fill="#4a4a6a" />
  <!-- ... eyes, smile, cheeks ... -->
</svg>
```

```javascript
// Source: MDN SVG <use> element + setAttribute
function swapPart(category, variantId) {
  const useEl = document.getElementById(`active-${category}`);
  useEl.setAttribute("href", `#${variantId}`);
}

// Usage:
swapPart("tail", "tail-2");  // Swaps to tail variant 2
swapPart("hair", "hair-3");  // Swaps to hair variant 3
swapPart("acc", "acc-1");    // Adds crown accessory
```

### Pattern 2: Color Recoloring via Fill Attribute

**What:** When user taps a color swatch, change the `fill` attribute on the active part's source `<g>` element (the one in `<defs>`). Because `<use>` clones the referenced element, and fill is an inherited SVG presentation attribute, the color propagates to all child paths.

**When to use:** For DRSS-05 (color swatch recoloring).

**Important nuance:** Setting `fill` on the `<use>` element itself works via CSS inheritance -- child elements that do not explicitly set their own fill will inherit from the `<use>`. However, elements inside `<defs>` that have explicit `fill` attributes will NOT be overridden by the `<use>` parent's fill. Two approaches:

**Approach A (recommended): Modify fill on the source `<g>` in `<defs>` directly.**
```javascript
// Source: MDN SVG fill attribute inheritance
function recolorPart(category, color) {
  // Get the current variant ID from the <use> element
  const useEl = document.getElementById(`active-${category}`);
  const variantId = useEl.getAttribute("href").slice(1); // remove #
  // Modify the source definition
  const sourceGroup = document.getElementById(variantId);
  // Update all fill-bearing children
  sourceGroup.querySelectorAll("[fill]").forEach((el) => {
    // Store original fill if not already stored (for undo)
    if (!el.dataset.originalFill) {
      el.dataset.originalFill = el.getAttribute("fill");
    }
    el.setAttribute("fill", color);
  });
}
```

**Approach B (simpler but less flexible): Design SVG variants without explicit fills, use CSS custom properties.**
```css
#active-tail { --part-fill: #7ec8c8; }
```
```xml
<g id="tail-1">
  <path d="..." fill="var(--part-fill, #7ec8c8)" />
</g>
```
This approach requires designing the SVG specifically for CSS variable support. Use Approach A for maximum compatibility with hand-crafted SVG art.

### Pattern 3: Command Stack Undo

**What:** Each user action (swap part, change color) creates a command object with an `undo()` function and pushes it onto a stack. The undo button pops the last command and calls `undo()`.

**When to use:** For DRSS-06 (undo).

**Example:**
```javascript
// Source: Command pattern (dev.to/npbee, tahazsh.com)
const undoStack = [];

function pushUndo(undoFn) {
  undoStack.push({ undo: undoFn });
}

function undo() {
  const cmd = undoStack.pop();
  if (cmd) cmd.undo();
}

// Usage in part swap:
function swapPartWithUndo(category, newVariantId) {
  const useEl = document.getElementById(`active-${category}`);
  const previousId = useEl.getAttribute("href");

  useEl.setAttribute("href", `#${newVariantId}`);

  pushUndo(() => {
    useEl.setAttribute("href", previousId);
  });
}

// Usage in color change:
function recolorWithUndo(category, newColor) {
  const useEl = document.getElementById(`active-${category}`);
  const variantId = useEl.getAttribute("href").slice(1);
  const sourceGroup = document.getElementById(variantId);
  const elements = sourceGroup.querySelectorAll("[fill]");

  // Capture current fills
  const previousFills = Array.from(elements).map((el) => ({
    el,
    fill: el.getAttribute("fill"),
  }));

  // Apply new color
  elements.forEach((el) => el.setAttribute("fill", newColor));

  pushUndo(() => {
    previousFills.forEach(({ el, fill }) => el.setAttribute("fill", fill));
  });
}
```

### Pattern 4: Selection Panel UI

**What:** A horizontal scrollable panel at the bottom of the screen (above the nav bar) with category tabs (tail, hair, accessory, color) and option thumbnails. Each thumbnail is a 60pt+ tap target.

**When to use:** The primary UI for DRSS-02 through DRSS-05.

**Layout:**
```
+------------------------------------------+
|                                          |
|          Mermaid SVG Display             |
|          (takes most of screen)          |
|                                          |
+------------------------------------------+
| [Tail] [Hair] [Acc] [Color] | [Undo]    |  <-- Category tabs
+------------------------------------------+
| [opt1] [opt2] [opt3] [opt4]             |  <-- Options row (scrollable)
+------------------------------------------+
| [home] [dressup] [coloring]             |  <-- Nav bar (existing)
+------------------------------------------+
```

**Example:**
```html
<div class="dressup-view">
  <div class="mermaid-container">
    <!-- SVG goes here -->
  </div>
  <div class="selection-panel">
    <div class="category-tabs">
      <button class="cat-tab active" data-category="tail">
        <!-- small tail icon SVG -->
      </button>
      <button class="cat-tab" data-category="hair">
        <!-- small hair icon SVG -->
      </button>
      <button class="cat-tab" data-category="acc">
        <!-- small accessory icon SVG -->
      </button>
      <button class="cat-tab" data-category="color">
        <!-- palette icon SVG -->
      </button>
      <button class="undo-btn" aria-label="Undo">
        <!-- undo arrow icon SVG -->
      </button>
    </div>
    <div class="options-row">
      <!-- Dynamically populated based on active category -->
    </div>
  </div>
</div>
```

### Pattern 5: Completion Detection and Celebration

**What:** Track which categories have user-selected values. When tail, hair, AND accessory all have non-default selections, trigger a celebration sparkle.

**When to use:** For DRSS-07.

**Example:**
```javascript
// Source: extended from existing sparkle.js
const state = {
  tail: "tail-1",    // default
  hair: "hair-1",    // default
  acc: "acc-none",   // no accessory
};

function checkCompletion() {
  const isComplete =
    state.tail !== "tail-1" &&
    state.hair !== "hair-1" &&
    state.acc !== "acc-none";

  if (isComplete) {
    triggerCelebration();
  }
}

function triggerCelebration() {
  const svg = document.getElementById("mermaid-svg");
  // Fire multiple sparkle bursts across the mermaid
  const centerX = 200;  // SVG viewBox center
  const positions = [
    { x: centerX, y: 80 },   // head
    { x: centerX, y: 250 },  // body
    { x: centerX, y: 500 },  // tail
  ];

  positions.forEach((pos, i) => {
    setTimeout(() => {
      for (let j = 0; j < 12; j++) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", String(pos.x + (Math.random() - 0.5) * 80));
        circle.setAttribute("cy", String(pos.y + (Math.random() - 0.5) * 80));
        circle.setAttribute("r", String(3 + Math.random() * 5));
        circle.setAttribute("fill", ["gold", "#ff69b4", "#87ceeb", "#dda0dd"][j % 4]);
        circle.classList.add("sparkle", "celebration");
        svg.appendChild(circle);
        setTimeout(() => circle.remove(), 1000);
      }
    }, i * 150);
  });
}
```

### Anti-Patterns to Avoid

- **Separate SVG files per variant:** Loading multiple SVG files means network requests and complexity. Embed all variants in one SVG file using `<defs>`.
- **Using `innerHTML` to swap SVG content:** Destroys and recreates DOM nodes, breaking event listeners and causing flicker. Use `setAttribute("href", ...)` on `<use>` elements instead.
- **Storing state in DOM attributes:** Keep a JS state object as the source of truth. The DOM reflects state, not the other way around.
- **Complex state management library:** For 3 categories with 3-4 options each plus an undo stack, a plain JS object + array is sufficient. No Redux, no MobX, no signals library.
- **Animating with JavaScript loops:** Continue using CSS `@keyframes` for sparkle/celebration animations. JS animation loops are unnecessary and janky on iPad.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SVG part variant management | Custom DOM cloning/replacement | `<defs>` + `<use href>` swap | Native SVG pattern, one setAttribute call, no DOM tree surgery |
| Color cascading to child elements | Manual querySelectorAll loop to recolor each path | `setAttribute("fill")` on parent `<g>` | SVG fill inherits to children; only needed if children have explicit fills |
| Undo/redo framework | Custom event sourcing system | Simple array push/pop with closures | Only need single-level undo, no persistence, no redo -- array is perfect |
| Sparkle celebration animation | Canvas particle system or external library | Existing sparkle.js pattern scaled up | Already proven to work on iPad Safari with CSS @keyframes |
| Touch-friendly selection UI | Custom gesture recognition | Standard `pointerdown` events on `<button>` elements | Buttons already handle touch correctly; just need 60pt+ sizing |

**Key insight:** Phase 2 is entirely a frontend JS + SVG problem. No new backend routes, no new libraries, no new server capabilities. The entire implementation lives in the frontend directory.

## Common Pitfalls

### Pitfall 1: `<use>` Elements and Fill Inheritance

**What goes wrong:** Setting fill on a `<use>` element doesn't change the color of the rendered content.
**Why it happens:** SVG `<use>` creates a shadow DOM clone. If the source elements in `<defs>` have explicit `fill` attributes, those override any inherited fill from the `<use>` parent.
**How to avoid:** Either (a) design variant SVGs without explicit fills and rely on inheritance, or (b) modify the fill attributes directly on the source elements inside `<defs>`. Option (b) is more robust for hand-crafted SVGs.
**Warning signs:** Color swatches appear to do nothing when tapped.

### Pitfall 2: SVG `<use>` and Pointer Events

**What goes wrong:** Tap events on `<use>` elements don't fire, or `event.target` returns unexpected elements.
**Why it happens:** The `<use>` element creates a shadow DOM clone. In some browsers, `event.target` may point to the shadow content rather than the `<use>` element itself.
**How to avoid:** Use `event.target.closest("[data-region]")` which traverses up to find the attributed element. Set `pointer-events="all"` on the `<use>` element. The existing `touch.js` already uses this `closest()` pattern.
**Warning signs:** Tapping on the mermaid registers different targets inconsistently.

### Pitfall 3: Selection Panel Covering the Mermaid

**What goes wrong:** The selection panel, category tabs, and nav bar together consume too much vertical space, squishing the mermaid display.
**Why it happens:** iPad in portrait has ~1366px height. Nav bar is 80px. If the selection panel is another 160px+, only ~1126px remain. With padding, the mermaid gets squeezed.
**How to avoid:** Keep the selection panel compact: one row of category tabs (60px) + one row of option buttons (80px) = 140px total. Combined with 80px nav bar = 220px for UI chrome, leaving 1146px for the mermaid. That is plenty.
**Warning signs:** Mermaid appears tiny or requires scrolling to see fully.

### Pitfall 4: Undo Stack Bloat

**What goes wrong:** Memory grows unbounded as the child taps hundreds of times.
**Why it happens:** No limit on undo stack size.
**How to avoid:** Cap the undo stack at 20-30 items. When a new action exceeds the limit, `shift()` the oldest entry.
**Warning signs:** App becomes sluggish after extended play.

### Pitfall 5: Color Recoloring Affects All Variants

**What goes wrong:** Recoloring the active tail also changes the colors of the other tail variants, so switching to a different tail shows it in the wrong color.
**Why it happens:** Modifying fill attributes on the source `<g>` in `<defs>` is a global mutation -- those elements are shared definitions.
**How to avoid:** When recoloring, track color overrides in the JS state object rather than mutating `<defs>`. Apply the color override each time a part is swapped in. The undo command should also restore the previous color.
**Warning signs:** Switching to a previously unselected tail variant shows it in a custom color instead of its original color.

### Pitfall 6: Default/Original Colors Lost

**What goes wrong:** After recoloring and undoing, the original SVG colors are permanently lost.
**Why it happens:** Not storing original fill values before overwriting them.
**How to avoid:** Store original fills in `data-original-fill` attributes on first recolor, or maintain a `defaultColors` map in JS state initialized from the SVG on load.
**Warning signs:** Undo appears to work but colors are slightly wrong.

## Code Examples

### Complete Dress-Up State Module
```javascript
// dressup.js -- dress-up state management, part swapping, color, undo
// Source: custom implementation following patterns from Phase 1 codebase

const SVG_NS = "http://www.w3.org/2000/svg";

// Part variant definitions
const PARTS = {
  tail: ["tail-1", "tail-2", "tail-3"],
  hair: ["hair-1", "hair-2", "hair-3"],
  acc: ["acc-none", "acc-1", "acc-2", "acc-3"],
};

// Color palette -- 10 preset swatches, child-friendly
const COLORS = [
  "#7ec8c8",  // ocean teal (default tail)
  "#c4a7d7",  // lavender (default hair)
  "#ff69b4",  // hot pink
  "#ffd700",  // gold
  "#87ceeb",  // sky blue
  "#98fb98",  // pale green
  "#ff6347",  // tomato red
  "#dda0dd",  // plum
  "#ffa07a",  // light salmon
  "#40e0d0",  // turquoise
];

// State
const state = {
  tail: "tail-1",
  hair: "hair-1",
  acc: "acc-none",
  activeCategory: "tail",
  colors: {},      // { "tail-1": "#7ec8c8", ... } overrides
};

const undoStack = [];
const MAX_UNDO = 30;

// -- Core operations --

export function swapPart(category, variantId) {
  const useEl = document.getElementById(`active-${category}`);
  const prevId = useEl.getAttribute("href").slice(1);
  if (prevId === variantId) return; // no-op

  useEl.setAttribute("href", `#${variantId}`);

  // Re-apply color override if one exists for this variant
  const savedColor = state.colors[variantId];
  if (savedColor) {
    applyColorToSource(variantId, savedColor);
  }

  const prevColor = state.colors[prevId];
  state[category] = variantId;

  pushUndo(() => {
    useEl.setAttribute("href", `#${prevId}`);
    state[category] = prevId;
    if (prevColor) applyColorToSource(prevId, prevColor);
  });

  checkCompletion();
}

export function recolorActivePart(color) {
  const category = state.activeCategory;
  if (category === "color") return; // color tab has no "active part"
  const variantId = state[category];
  if (!variantId || variantId === "acc-none") return;

  const prevColor = state.colors[variantId] || getOriginalColor(variantId);
  state.colors[variantId] = color;
  applyColorToSource(variantId, color);

  pushUndo(() => {
    if (prevColor) {
      state.colors[variantId] = prevColor;
      applyColorToSource(variantId, prevColor);
    }
  });
}

export function undo() {
  const cmd = undoStack.pop();
  if (cmd) cmd.undo();
}

// -- Helpers --

function applyColorToSource(variantId, color) {
  const source = document.getElementById(variantId);
  if (!source) return;
  source.querySelectorAll("path, circle, ellipse, rect").forEach((el) => {
    const fill = el.getAttribute("fill");
    if (fill && fill !== "none") {
      el.setAttribute("fill", color);
    }
  });
}

function getOriginalColor(variantId) {
  const source = document.getElementById(variantId);
  if (!source) return null;
  const firstFilled = source.querySelector("[fill]:not([fill='none'])");
  return firstFilled ? firstFilled.getAttribute("fill") : null;
}

function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) undoStack.shift();
}

function checkCompletion() {
  if (state.tail !== "tail-1" && state.hair !== "hair-1" && state.acc !== "acc-none") {
    triggerCelebration();
  }
}

export { PARTS, COLORS, state };
```

### Selection Panel HTML Structure
```html
<!-- Generated by renderDressUp() in app.js -->
<div class="dressup-view">
  <div class="mermaid-container" id="mermaid-container">
    <!-- mermaid SVG inserted here -->
  </div>
  <div class="selection-panel">
    <div class="category-tabs">
      <button class="cat-tab active" data-category="tail" aria-label="Tails">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M12,2 Q8,10 6,16 Q10,20 12,18 Q14,20 18,16 Q16,10 12,2Z"
                fill="#7ec8c8" />
        </svg>
      </button>
      <button class="cat-tab" data-category="hair" aria-label="Hair">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M6,12 Q6,4 12,3 Q18,4 18,12 Q16,8 12,7 Q8,8 6,12Z"
                fill="#c4a7d7" />
        </svg>
      </button>
      <button class="cat-tab" data-category="acc" aria-label="Accessories">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M12,2 L14,8 L20,8 L15,12 L17,18 L12,14 L7,18 L9,12 L4,8 L10,8Z"
                fill="#ffd700" />
        </svg>
      </button>
      <button class="cat-tab" data-category="color" aria-label="Colors">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" fill="none" stroke="#999" stroke-width="2" />
          <circle cx="8" cy="10" r="3" fill="#ff69b4" />
          <circle cx="16" cy="10" r="3" fill="#87ceeb" />
          <circle cx="12" cy="16" r="3" fill="#98fb98" />
        </svg>
      </button>
      <button class="undo-btn" aria-label="Undo">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path d="M7,12 L3,8 L7,4 M3,8 L15,8 Q20,8 20,14 Q20,20 15,20 L10,20"
                fill="none" stroke="#888" stroke-width="2.5" stroke-linecap="round" />
        </svg>
      </button>
    </div>
    <div class="options-row" id="options-row">
      <!-- Populated dynamically based on active category -->
    </div>
  </div>
</div>
```

### Selection Panel CSS
```css
/* Selection panel */
.selection-panel {
  position: absolute;
  bottom: 80px;  /* above nav bar */
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.category-tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 4px 8px;
}

.cat-tab, .undo-btn {
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

.cat-tab.active {
  border-color: #5b8fa8;
  background: rgba(100, 200, 255, 0.2);
}

.undo-btn {
  margin-left: auto;  /* push to right */
}

.options-row {
  display: flex;
  gap: 8px;
  padding: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  justify-content: center;
}

.option-btn {
  width: 64px;
  height: 64px;
  min-width: 64px;
  min-height: 64px;
  border: 2px solid transparent;
  border-radius: 14px;
  background: rgba(200, 220, 240, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: manipulation;
  cursor: pointer;
}

.option-btn.selected {
  border-color: #c47ed0;
  background: rgba(196, 126, 208, 0.15);
}

/* Color swatches */
.color-swatch {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* Celebration sparkle (enhanced) */
.sparkle.celebration {
  animation: celebration-sparkle 1s ease-out forwards;
}

@keyframes celebration-sparkle {
  0% { opacity: 1; transform: scale(0); }
  30% { opacity: 1; transform: scale(1.5); }
  100% { opacity: 0; transform: scale(0.3) translateY(-30px); }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Image layers (PNG/GIF overlays) | SVG `<defs>` + `<use>` for variants | Always available in SVG | No separate image files, instant swap, vector-quality at any resolution |
| jQuery `.show()`/`.hide()` | `setAttribute("href", ...)` on `<use>` | 2018+ (modern JS) | One DOM operation instead of three; no jQuery dependency |
| Complex state management (Redux) | Plain JS object + undo array | Always valid for small scope | Zero overhead; sufficient for 3 categories x 4 options |
| Memento pattern (full state snapshots) | Command pattern (closure per action) | Both are valid | Command closures capture exactly what changed; smaller memory footprint |

**Deprecated/outdated:**
- **`xlink:href` on `<use>` elements:** SVG 2 uses plain `href`. Safari supports `href` since Safari 12 (2018). No need for `xlink:href` namespace.

## Open Questions

1. **SVG Art Asset Quality**
   - What we know: Phase 1 created a hand-crafted proof-of-concept mermaid SVG with 3 regions. Phase 2 needs 3-4 distinct visual variants for each of tail, hair, and accessory.
   - What's unclear: Whether the SVG art will be hand-crafted (guaranteed structure) or AI-generated then edited. AI-generated art traced with vtracer may not produce clean enough variant shapes.
   - Recommendation: Hand-craft all SVG variants, following the existing mermaid.svg structure. This is a small amount of art (about 10 variant groups) and hand-crafting guarantees clean `<g>` groups with proper `data-region` attributes.

2. **Color Recoloring Granularity**
   - What we know: Each variant group contains multiple paths with different fills (e.g., tail has main body, scales, fin -- each a slightly different shade).
   - What's unclear: Should recoloring change ALL fills to the same color (monochrome), or should it shift all fills relative to the chosen base color (preserving tonal variation)?
   - Recommendation: Use a simple approach -- change the primary fill to the selected color, and adjust accent fills to a lighter/darker shade of that color. This preserves visual depth without complex color math. A simple `lighten()` helper (mix with white) and `darken()` helper (mix with black) on hex colors is sufficient.

3. **"Default" vs "Customized" State for Completion Check**
   - What we know: DRSS-07 says sparkle when "all parts are selected." The mermaid loads with default parts visible.
   - What's unclear: Does the default count as "selected"? Or must the child actively change each part?
   - Recommendation: Require active changes -- the child must have tapped at least one non-default option for each of tail, hair, and accessory. This makes the celebration meaningful.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8+ with pytest-playwright 0.7.2 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/ -x` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DRSS-01 | Base mermaid visible on dress-up screen | e2e | `uv run pytest tests/test_dressup.py::TestDressUpView::test_mermaid_visible -x` | -- Wave 0 |
| DRSS-02 | Tapping tail option swaps tail (3-4 options) | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_tail_swap -x` | -- Wave 0 |
| DRSS-03 | Tapping hair option swaps hair (3-4 options) | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_hair_swap -x` | -- Wave 0 |
| DRSS-04 | Tapping accessory option adds/swaps (3-4) | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_accessory_swap -x` | -- Wave 0 |
| DRSS-05 | Color swatch recolors selected part (8-12 colors) | e2e | `uv run pytest tests/test_dressup.py::TestColorRecolor::test_color_swatch_changes_fill -x` | -- Wave 0 |
| DRSS-06 | Undo button reverts last change | e2e | `uv run pytest tests/test_dressup.py::TestUndo::test_undo_reverts_swap -x` | -- Wave 0 |
| DRSS-07 | Sparkle when all parts selected | e2e | `uv run pytest tests/test_dressup.py::TestCompletion::test_celebration_sparkle -x` | -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_dressup.py` -- Playwright E2E tests for all DRSS requirements
- [ ] Existing `tests/test_e2e.py` -- may need updates if `renderDressUp()` changes significantly (currently tests SVG fetch + data-region presence)

## Sources

### Primary (HIGH confidence)
- [MDN SVG `<use>` element](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/use) - `<use>` with `href` attribute for referencing `<defs>` elements, shadow DOM cloning behavior
- [MDN SVG fill attribute](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/fill) - Fill inheritance on `<g>` groups, cascading to child elements, presentation attribute behavior
- [MDN SVG visibility attribute](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/visibility) - `display: none` vs `visibility: hidden` for SVG elements
- [MDN pointer-events SVG](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/pointer-events) - `pointer-events="all"` on interactive elements, shadow DOM behavior
- Existing codebase: `frontend/js/touch.js`, `frontend/js/sparkle.js`, `frontend/assets/svg/mermaid.svg` -- established patterns for SVG interaction and animation

### Secondary (MEDIUM confidence)
- [Command-based undo for JS apps (dev.to)](https://dev.to/npbee/command-based-undo-for-js-apps-34d6) - Command pattern undo stack with `exec()` and `undo()` methods
- [Undo with command pattern (tahazsh.com)](https://tahazsh.com/blog/undo-with-command-pattern/) - CommandManager class, closure-based undo
- [Dynamic SVGs using defs (metaskills.net)](https://metaskills.net/2014/08/29/dynamic-svgs-using-defs-elements-and-javascript/) - Pattern for `<defs>` + `<use>` dynamic creation with JavaScript
- [Changing SVG colors with JS (kirupa.com)](https://www.kirupa.com/web/changing_colors_svg_css_javascript.htm) - `setAttribute("fill", color)` patterns, CSS vs attribute precedence
- [SVG `use` with external source (CSS-Tricks)](https://css-tricks.com/svg-use-external-source/) - `href` vs deprecated `xlink:href`
- [Dress-up game vanilla JS (GitHub)](https://github.com/hazieon/dressupgame) - Vanilla JS dress-up game architecture reference

### Tertiary (LOW confidence)
- Color recoloring with tonal variation (preserving light/dark shades when changing base color) -- no authoritative source found; implementation will need empirical testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies; vanilla JS + SVG DOM APIs are extremely well-documented browser standards
- Architecture (`<defs>` + `<use>` swap): HIGH - SVG `<use>` is a core SVG feature documented by W3C and MDN; href swap is a single setAttribute call
- Undo pattern: HIGH - Command stack is a textbook pattern; implementation is ~20 lines of JS
- Color recoloring: MEDIUM - Basic setAttribute("fill") is HIGH confidence, but tonal variation (preserving shade differences within a part) needs empirical testing
- Completion animation: HIGH - Direct extension of existing sparkle.js, same CSS @keyframes approach
- Selection panel UI: HIGH - Standard HTML buttons with CSS flexbox, same 60pt+ tap target pattern from Phase 1

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable browser APIs, no fast-moving dependencies)
