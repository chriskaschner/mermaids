# Phase 5: Flood-Fill Coloring - Research

**Researched:** 2026-03-09
**Domain:** HTML5 Canvas flood fill, Canvas+SVG hybrid rendering, iPad Safari memory management
**Confidence:** HIGH

## Summary

This phase replaces the existing SVG region-based coloring (data-region tap-to-fill) with a canvas-based flood fill and SVG line art overlay. The architecture is: rasterize the SVG onto an HTML5 canvas for pixel-level flood fill, then overlay the original SVG on top (via CSS absolute positioning) so line art stays crisp at retina resolution. The SVG overlay has `pointer-events: none` so taps pass through to the canvas.

The flood fill algorithm should use a scanline approach operating on `getImageData` / `putImageData`. The key technical challenge is anti-aliased edge handling -- vtracer-generated SVGs rasterize with anti-aliased edges, so the flood fill needs a configurable color tolerance (around 32-64 for this use case) to stop at line boundaries without bleeding through. Undo is implemented via ImageData snapshots stored in a capped stack.

**Primary recommendation:** Hand-roll a scanline flood fill (~80 lines of JS) with tolerance parameter. No npm/bundler exists in this project -- all frontend JS is vanilla ES modules loaded via `<script type="module">`. Using a library would require either a bundler setup or copy-pasting, and the algorithm is straightforward enough to implement directly.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Tapping any region (white or already colored) fills it with the currently selected color -- overwrite is allowed
- Attempt a quick spread animation (~200ms) where color visibly spreads outward from the tap point
- If the spread animation causes performance issues on iPad, fall back to instant fill -- performance wins over animation
- Undo button should be visually disabled (grayed out) when the undo stack is empty
- Keep the existing 10 preset color swatches (ocean teal, lavender, hot pink, gold, sky blue, pale green, tomato red, plum, light salmon, turquoise)
- Same palette as dress-up -- consistency across activities

### Claude's Discretion
- Fill visual feedback (sparkle, opacity pulse, or none) -- pick what feels delightful without slowing interaction
- Swatch layout (bottom panel vs side panel) -- pick best layout for iPad landscape/portrait
- Selected color indicator styling
- Undo depth (30 cap vs unlimited) -- balance iPad memory constraints with usability
- Whether to include a "clear all" reset button alongside undo
- Progress persistence when navigating back to gallery (lost vs preserved in session)
- Gallery thumbnail indicators for colored pages
- Navigation warning when switching to dress-up (no warning vs gentle hint) -- audience is a 6-year-old

### Deferred Ideas (OUT OF SCOPE)
- Rainbow color swatch with color picker (full color wheel / custom color selection) -- future phase or v2 feature
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CLRV-01 | Coloring pages use canvas-based flood fill at tap point (replaces region-based fill) | Scanline flood fill on canvas ImageData; SVG rasterized via Image+drawImage; pointerdown tap coordinates mapped to canvas pixel space |
| CLRV-02 | SVG line art overlays canvas for crisp retina-quality outlines | SVG element positioned absolutely over canvas with pointer-events:none; both sized identically; SVG at device pixel ratio for retina |
| CLRV-03 | Flood fill handles anti-aliased edges with configurable tolerance | Tolerance parameter (0-255) in color comparison; recommended default 32-64; compares RGBA channel differences against threshold |
| CLRV-04 | Canvas memory is released when navigating away from coloring (iPad Safari safety) | Set canvas width/height to 0, null context reference, remove canvas element from DOM on route change |
| CLRV-05 | Undo reverts last flood-fill operation via ImageData snapshots | Push ctx.getImageData() before each fill; undo pops and calls ctx.putImageData(); cap stack at 30 (each snapshot ~4MB for 1024x1024) |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vanilla JS (ES modules) | ES2020+ | All frontend code | Project pattern -- no bundler, no npm, `<script type="module">` in index.html |
| Canvas 2D API | Browser native | Flood fill pixel manipulation | getImageData/putImageData for pixel-level access |
| SVG (inline) | Browser native | Crisp line art overlay | Already used in project; vtracer output is SVG |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None | - | - | This phase uses zero external libraries |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled flood fill | q-floodfill (npm) | Would need bundler or UMD copy; 1.8k gzipped, good perf (30-40ms on 800x660), but project has no npm setup |
| Hand-rolled flood fill | floodfill.js (npm) | Adds to window.CanvasRenderingContext2D.prototype; tolerance support built in; but same npm problem |
| ImageData undo snapshots | Canvas toDataURL snapshots | toDataURL is slower, creates strings; ImageData is raw typed array, faster to save/restore |

**Installation:**
```bash
# No installation needed -- vanilla JS, no dependencies
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/js/
  floodfill.js       # NEW: scanline flood fill algorithm + tolerance
  coloring.js        # REWRITE: canvas-based state management, undo via ImageData
  app.js             # MODIFY: openColoringPage() sets up canvas+SVG hybrid
  sparkle.js         # REUSE: tap feedback (may need canvas coordinate adaptation)
  touch.js           # NOT USED by coloring anymore (was SVG-specific)
frontend/css/
  style.css          # MODIFY: canvas+SVG overlay positioning, undo disabled state
```

### Pattern 1: Canvas + SVG Overlay
**What:** Layer a canvas element (for pixel fills) underneath an SVG element (for crisp lines), both absolutely positioned in a relative container. The SVG has `pointer-events: none` so taps hit the canvas.
**When to use:** When you need pixel-level manipulation (flood fill) but also want vector-quality line art.
**Example:**
```html
<!-- Container with relative positioning -->
<div class="coloring-page-container" style="position: relative;">
  <!-- Canvas layer: receives taps, holds colored pixels -->
  <canvas id="coloring-canvas" width="1024" height="1024"
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></canvas>
  <!-- SVG overlay: crisp lines, no pointer events -->
  <svg viewBox="0 0 1024 1024"
       style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    <!-- line art paths from the coloring page SVG -->
  </svg>
</div>
```

### Pattern 2: SVG-to-Canvas Rasterization
**What:** Load the SVG as an Image, draw it onto the canvas with `drawImage()`, then use the canvas for flood fill. The SVG overlay on top shows the same line art but at vector quality.
**When to use:** To initialize the canvas with a white-background rasterized version of the SVG art.
**Example:**
```javascript
// Source: standard Canvas API pattern
async function rasterizeSVGToCanvas(svgUrl, canvas) {
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  // Fill canvas white first (flood fill needs a base color)
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const img = new Image();
  img.src = svgUrl;
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
}
```

### Pattern 3: Scanline Flood Fill with Tolerance
**What:** Non-recursive flood fill that processes horizontal scanlines, pushing only scanline endpoints onto a stack. Tolerance parameter allows filling through anti-aliased edge pixels.
**When to use:** For any canvas flood fill operation.
**Example:**
```javascript
// Scanline flood fill operating on ImageData
function floodFill(imageData, startX, startY, fillColor, tolerance) {
  const { data, width, height } = imageData;
  const visited = new Uint8Array(width * height);
  const stack = [];

  const idx = (x, y) => (y * width + x) * 4;
  const startIdx = idx(startX, startY);
  const startR = data[startIdx], startG = data[startIdx+1];
  const startB = data[startIdx+2], startA = data[startIdx+3];

  function colorMatch(i) {
    return Math.abs(data[i] - startR) <= tolerance &&
           Math.abs(data[i+1] - startG) <= tolerance &&
           Math.abs(data[i+2] - startB) <= tolerance &&
           Math.abs(data[i+3] - startA) <= tolerance;
  }

  // Parse fill color (hex to RGBA)
  const [fr, fg, fb] = hexToRgb(fillColor);

  // If start pixel already matches fill color, skip
  if (data[startIdx] === fr && data[startIdx+1] === fg && data[startIdx+2] === fb) return;

  stack.push([startX, startY]);

  while (stack.length > 0) {
    let [x, y] = stack.pop();
    let pixIdx = y * width + x;

    // Move left to find scanline start
    while (x > 0 && !visited[pixIdx - 1] && colorMatch(idx(x - 1, y))) {
      x--; pixIdx--;
    }

    let spanAbove = false, spanBelow = false;

    // Scan right across the scanline
    while (x < width && !visited[pixIdx] && colorMatch(idx(x, y))) {
      const i = idx(x, y);
      data[i] = fr; data[i+1] = fg; data[i+2] = fb; data[i+3] = 255;
      visited[pixIdx] = 1;

      // Check pixel above
      if (y > 0) {
        const above = !visited[pixIdx - width] && colorMatch(idx(x, y - 1));
        if (above && !spanAbove) { stack.push([x, y - 1]); spanAbove = true; }
        else if (!above) { spanAbove = false; }
      }
      // Check pixel below
      if (y < height - 1) {
        const below = !visited[pixIdx + width] && colorMatch(idx(x, y + 1));
        if (below && !spanBelow) { stack.push([x, y + 1]); spanBelow = true; }
        else if (!below) { spanBelow = false; }
      }
      x++; pixIdx++;
    }
  }
}
```

### Pattern 4: Pointer-to-Canvas Coordinate Mapping
**What:** Convert CSS pointer event coordinates to canvas pixel coordinates, accounting for the canvas being scaled via CSS (display size != pixel size).
**When to use:** Every tap on the canvas.
**Example:**
```javascript
canvas.addEventListener('pointerdown', (e) => {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const x = Math.floor((e.clientX - rect.left) * scaleX);
  const y = Math.floor((e.clientY - rect.top) * scaleY);
  // x, y are now canvas pixel coordinates
});
```

### Pattern 5: ImageData Undo Stack
**What:** Before each fill, snapshot the entire canvas via `getImageData()`. Store snapshots in a capped array. Undo pops and calls `putImageData()`.
**When to use:** For undo support in canvas painting operations.
**Example:**
```javascript
const MAX_UNDO = 30;
const undoStack = [];

function pushUndoSnapshot(ctx, canvas) {
  undoStack.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
  if (undoStack.length > MAX_UNDO) undoStack.shift();
}

function undo(ctx, canvas) {
  const snapshot = undoStack.pop();
  if (snapshot) ctx.putImageData(snapshot, 0, 0);
}
```

### Anti-Patterns to Avoid
- **Recursive flood fill:** Will cause stack overflow on large regions. Use iterative scanline approach.
- **Getting/putting single pixels:** `getImageData` for one pixel at a time is extremely slow. Always get the full image data once, manipulate the typed array, then put it back once.
- **Skipping `willReadFrequently`:** Without this hint, Chrome will auto-disable GPU acceleration after 2 reads, causing inconsistent performance. Set it explicitly on context creation.
- **Forgetting canvas cleanup on navigation:** iPad Safari enforces a 384MB total canvas memory limit. Leaving canvas elements in the DOM accumulates memory.
- **Using `toDataURL()` for undo:** String encoding is far slower than raw ImageData snapshots.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Color hex parsing | Custom regex parser | Standard `parseInt(hex.slice(1,3), 16)` pattern | Well-known, one-liner |
| Canvas coordinate mapping | Complex matrix math | `getBoundingClientRect()` + scale factors | Handles CSS scaling, device pixel ratio |
| SVG loading | XMLHttpRequest with manual parsing | `fetch()` + Image element `src` | Modern, clean, handles caching |
| Animation timing | `setInterval` | `requestAnimationFrame` | Syncs with display refresh, auto-pauses |

**Key insight:** The flood fill algorithm itself IS worth hand-rolling (~80 lines) because the project has no npm/bundler infrastructure. Everything else (coordinate mapping, color parsing, image loading) uses standard browser APIs.

## Common Pitfalls

### Pitfall 1: Anti-Aliased Edge Bleeding
**What goes wrong:** Flood fill bleeds through line art boundaries because anti-aliased edges contain semi-transparent pixels that don't exactly match the fill-target color.
**Why it happens:** vtracer SVGs rendered to canvas produce anti-aliased edges at line boundaries. With tolerance=0, fill stops at the first anti-aliased pixel, leaving visible white gaps. With tolerance too high, fill bleeds through thin lines.
**How to avoid:** Use a tolerance of 32-64. This fills through the anti-aliased gradient but stops at actual line art (which is typically black/dark, far from white). Test with the actual SVG files.
**Warning signs:** White halos around filled regions (tolerance too low) or color leaking into adjacent regions (tolerance too high).

### Pitfall 2: Canvas Size vs. Display Size Mismatch
**What goes wrong:** Canvas internal resolution doesn't match its CSS display size, causing blurry rendering or misaligned taps.
**Why it happens:** Canvas has two sizes: its pixel buffer (`width`/`height` attributes) and its CSS display size. If these don't match the aspect ratio, content stretches.
**How to avoid:** Set canvas `width` and `height` attributes to match the SVG viewBox (1024x1024). Use CSS to scale the display size. Calculate pointer coordinates using the scale ratio.
**Warning signs:** Flood fill lands in wrong spot relative to where user tapped.

### Pitfall 3: iPad Safari Canvas Memory Exhaustion
**What goes wrong:** App crashes or canvas goes blank after navigating between pages multiple times.
**Why it happens:** iPad Safari enforces a total canvas memory limit (~384MB on newer devices, lower on older). Each 1024x1024 RGBA canvas is ~4MB. Undo stack of 30 snapshots = ~120MB. If canvases aren't released, memory accumulates.
**How to avoid:** On navigation away: (1) set canvas.width = canvas.height = 0, (2) null the context reference, (3) remove canvas from DOM, (4) clear the undo stack. Cap undo at 30.
**Warning signs:** Console warning "Total canvas memory use exceeds the maximum limit."

### Pitfall 4: willReadFrequently Timing
**What goes wrong:** Canvas context created without `willReadFrequently: true`, then Chrome auto-disables GPU after first `getImageData` call, causing sudden performance drop.
**Why it happens:** Chrome has an undocumented heuristic that switches to software rendering after detecting 2+ canvas reads. Must be set at context creation time.
**How to avoid:** Always create context with `canvas.getContext('2d', { willReadFrequently: true })`. This is correct for flood fill (read-heavy) but note it trades write speed for read speed.
**Warning signs:** First fill is fast, subsequent fills get slower (Chrome only). Safari does not have this issue.

### Pitfall 5: SVG External References in Image
**What goes wrong:** SVG loaded as Image source can't load external resources (fonts, linked images), rendering incomplete line art.
**Why it happens:** Security restriction -- SVGs rendered via `<img>` or `drawImage()` are sandboxed.
**How to avoid:** The vtracer-generated SVGs are self-contained paths with no external references, so this should not be an issue. Verify SVGs don't reference external resources.
**Warning signs:** Missing parts in the rasterized canvas version that are visible in the SVG overlay.

### Pitfall 6: Spread Animation Performance on iPad
**What goes wrong:** Attempting to animate flood fill spread with multiple `putImageData` calls per frame causes janky, slow animation.
**Why it happens:** `putImageData` is not GPU-accelerated. Multiple calls per frame block the main thread.
**How to avoid:** If implementing spread animation: fill in chunks per `requestAnimationFrame`, putting image data once per frame. If performance is bad on iPad (target: < 200ms total), fall back to instant fill per user decision.
**Warning signs:** Fill animation takes > 500ms or causes visible frame drops.

## Code Examples

Verified patterns from official sources and project conventions:

### Canvas Context Setup with willReadFrequently
```javascript
// Source: WHATWG HTML spec, Chrome developer docs
const canvas = document.createElement('canvas');
canvas.width = 1024;
canvas.height = 1024;
const ctx = canvas.getContext('2d', { willReadFrequently: true });
```

### SVG Rasterization to Canvas
```javascript
// Source: MDN CanvasRenderingContext2D.drawImage()
function rasterizeSVG(svgUrl, canvas) {
  const ctx = canvas.getContext('2d');
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      // White background first
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // Draw SVG line art on top
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      resolve();
    };
    img.onerror = reject;
    img.src = svgUrl;
  });
}
```

### Hex Color to RGB
```javascript
function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
```

### Canvas Memory Cleanup
```javascript
// Source: WebKit bug tracker, Apple developer forums
function releaseCanvas(canvas) {
  if (!canvas) return;
  canvas.width = 0;
  canvas.height = 0;
  canvas.remove();
}
```

### Undo Button Disabled State (CSS)
```css
.undo-btn.disabled {
  opacity: 0.35;
  pointer-events: none;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SVG data-region tap-to-fill | Canvas flood fill + SVG overlay | This phase | Enables coloring any SVG, not just pre-tagged regions |
| Closure-based undo (function references) | ImageData snapshot undo | This phase | Works with pixel data instead of DOM attributes |
| Region-based fillRegion() | Scanline flood fill on ImageData | This phase | Pixel-level precision, tolerance for anti-aliasing |
| `getContext('2d')` | `getContext('2d', { willReadFrequently: true })` | Chrome ~2023, Safari 18 (2024) | Required for consistent performance with getImageData |

**Deprecated/outdated:**
- The existing `fillRegion()`, `getFillableElements()`, and the closure-based undo stack in `coloring.js` are fully replaced by canvas-based equivalents
- The `touch.js` module's SVG-specific event delegation pattern is not used for canvas coloring (canvas handles its own pointerdown)

## Open Questions

1. **Optimal tolerance value for vtracer SVGs**
   - What we know: Tolerance 32-64 is typical for anti-aliased edges. vtracer produces clean vector paths that rasterize with standard browser anti-aliasing.
   - What's unclear: The exact optimal value depends on line thickness and anti-aliasing behavior in Safari's SVG rasterizer.
   - Recommendation: Start with tolerance=32, expose as a constant for easy tuning. Test with all 4 coloring page SVGs.

2. **Spread animation feasibility on iPad**
   - What we know: User wants ~200ms spread animation from tap point. Each frame requires a partial `putImageData` call. iPad Safari has slower canvas write performance than Chrome.
   - What's unclear: Whether partial fills per frame will be fast enough on real iPad hardware.
   - Recommendation: Implement with chunked scanline rendering (N scanlines per frame via requestAnimationFrame). Include a performance check: if first frame takes > 50ms, abort animation and do instant fill.

3. **Canvas resolution: 1024x1024 vs device-scaled**
   - What we know: SVGs have viewBox 0 0 1024 1024. At 2x retina, that's 2048x2048 canvas = ~16MB per ImageData snapshot.
   - What's unclear: Whether 1024x1024 is crisp enough given the SVG overlay handles line crispness.
   - Recommendation: Use 1024x1024 for the canvas (fill colors don't need retina resolution since color regions are large areas). The SVG overlay at retina handles line crispness. This keeps undo snapshots at ~4MB each (30 * 4MB = 120MB, well within 384MB limit).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8+ with playwright (sync_api) |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/test_coloring.py -x` |
| Full suite command | `uv run pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CLRV-01 | Tap white region fills with selected color via canvas flood fill | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasFloodFill::test_tap_fills_region -x` | No -- Wave 0 |
| CLRV-02 | SVG line art overlays canvas, lines stay crisp | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasOverlay::test_svg_overlay_present -x` | No -- Wave 0 |
| CLRV-03 | Flood fill stops at anti-aliased edges | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasFloodFill::test_fill_stops_at_lines -x` | No -- Wave 0 |
| CLRV-04 | Canvas memory released on navigation | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasMemory::test_canvas_released_on_nav -x` | No -- Wave 0 |
| CLRV-05 | Undo reverts last fill via ImageData snapshot | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasUndo::test_undo_reverts_fill -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_coloring.py -x`
- **Per wave merge:** `uv run pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_coloring.py` -- FULL REWRITE needed: existing tests use SVG data-region pattern; new tests must verify canvas flood fill, SVG overlay, ImageData undo, canvas cleanup
- [ ] Existing test structure (conftest.py with live_server, iPad emulation, Playwright) is reusable as-is

## Sources

### Primary (HIGH confidence)
- WHATWG HTML Canvas spec -- getImageData, putImageData, willReadFrequently, canvas element lifecycle
- MDN CanvasRenderingContext2D.drawImage() -- SVG to canvas rasterization
- WebKit bug tracker #195325 -- iPad Safari canvas memory limits (384MB)
- Apple Developer Forums -- canvas memory cleanup pattern (width=0, height=0)
- Project codebase -- existing coloring.js, app.js, sparkle.js, touch.js, style.css, test_coloring.py

### Secondary (MEDIUM confidence)
- [q-floodfill GitHub](https://github.com/pavelkukov/q-floodfill) -- scanline algorithm reference, 30-40ms perf on 800x660
- [Canvas willReadFrequently analysis](https://www.schiener.io/2024-08-02/canvas-willreadfrequently) -- Chrome heuristic behavior, Safari compatibility
- [Ben Akrin flood fill](https://ben.akrin.com/an-html5-canvas-flood-fill-that-doesnt-kill-the-browser/) -- scanline approach #4 as optimal
- [Instant colour fill with Canvas](https://shaneosullivan.wordpress.com/2023/05/23/instant-colour-fill-with-html-canvas/) -- web worker pre-processing approach (reference only)

### Tertiary (LOW confidence)
- [PQINA canvas limits](https://pqina.nl/blog/total-canvas-memory-use-exceeds-the-maximum-limit/) -- older iOS memory limit numbers (224MB on older devices)
- [floodfill.js](https://github.com/binarymax/floodfill.js/) -- tolerance documentation (128 for anti-alias), not directly used

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - project has no npm/bundler, vanilla JS confirmed by reading all frontend files
- Architecture: HIGH - canvas+SVG hybrid is the established pattern per STATE.md decisions; coordinate mapping and ImageData patterns are well-documented browser APIs
- Pitfalls: HIGH - anti-aliasing tolerance, canvas memory limits, willReadFrequently behavior all verified across multiple sources
- Flood fill algorithm: HIGH - scanline approach well-documented, q-floodfill provides reference implementation, core algorithm is ~80 lines

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable browser APIs, no fast-moving dependencies)
