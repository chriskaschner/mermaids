# Phase 6: Dress-Up Art Swap - Research

**Researched:** 2026-03-09
**Domain:** SVG asset integration, defs+use variant swap, recoloring with vtracer-output SVGs
**Confidence:** HIGH

## Summary

Phase 6 replaces the hand-crafted mermaid SVG with AI-generated kawaii art while preserving the existing dress-up interaction (variant swapping + color recoloring). The core technical challenge is that vtracer-traced SVGs have fundamentally different fill patterns than hand-crafted SVGs: each traced variant contains hundreds of path elements with dozens of nearly-identical fill colors (e.g., tail-1.svg has 528 paths with hundreds of unique brown/tan hex values), plus a background rectangle covering the entire 1024x1024 canvas. The existing `applyColorToSource()` function already handles uniform recoloring of all fill-bearing elements, which is the correct approach for this kawaii flat-color style.

The second major work item is replacing inline hardcoded preview icons with actual traced SVG thumbnails loaded at runtime. Individual variant SVGs (28KB-115KB each) need to be deployed to `frontend/assets/svg/dressup/` and fetched on demand. Preview buttons grow from 24x24 to 48x48 SVG viewBox within 64x64px buttons (already meeting the 60pt touch target requirement).

**Primary recommendation:** The existing assembled mermaid.svg from Phase 4 already works with the defs+use mechanism. The main tasks are: (1) copy individual variant SVGs to frontend for preview thumbnails, (2) rewrite `getVariantPreviewSVG()` to fetch real SVGs, (3) verify recoloring works with the many-path traced output, and (4) evaluate body/face visual cohesion with AI-generated parts.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Uniform recolor: apply selected swatch color to ALL fill-bearing elements (current behavior preserved)
- Skip elements with fill="none" -- outlines/strokes keep their original color for kawaii line-art look
- Per-variant color memory: each variant remembers its own color override (state.colors[variantId]) -- switching variants restores their individual colors
- Face and body always stay fixed skin tone -- NOT recolorable. Only tail, hair, and accessories are recolorable categories
- Use scaled-down actual traced SVGs as preview thumbnails (not hardcoded simplified icons)
- Fetch variant SVGs from files at runtime (e.g., fetch dressup/tail-1.svg) rather than inlining in JS
- Preview button size: 48x48px (up from 24x24) -- meets 60pt+ touch target guideline for iPad
- Previews reflect applied color overrides: if user recolors tail-1 pink, its thumbnail also shows pink

### Claude's Discretion
- Whether AI-generated SVGs need regeneration/tuning for clean recoloring (evaluate and decide)
- Body/face approach: keep hardcoded or regenerate to match kawaii style (based on visual evaluation)
- Any CSS/layout adjustments needed for larger preview buttons in the options row

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DRSV-01 | Dress-up mermaid uses AI-generated kawaii art (replaces hand-crafted SVG) | The assembled mermaid.svg from Phase 4 pipeline already embeds traced AI-generated variants in defs. Needs deployment to frontend and verification that it renders correctly. |
| DRSV-02 | SVG defs+use variant swap works with new AI-generated part assets | The existing swapPart() sets `<use>` href to reference variant `<g>` in `<defs>`. Traced SVGs have been assembled into this structure by assemble.py. Background-rect paths need attention (first path is fill="#FEFEFE" covering 1024x1024). |
| DRSV-03 | Color recoloring works on kawaii flat-color style parts | applyColorToSource() already applies uniform color to all fill-bearing paths. Traced SVGs have no fill="none" elements. The many-color traced output will all get overridden uniformly, which is the desired behavior. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vanilla JS (ES modules) | N/A | Frontend interaction (dressup.js, app.js) | Established project pattern, no framework |
| Python xml.etree.ElementTree | stdlib | SVG assembly pipeline (assemble.py) | Already used in Phase 4 |
| vtracer | 0.6.12+ | PNG-to-SVG tracing | Already used in Phase 4 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| FastAPI | 0.115+ | Static file serving (dev server) | Always -- serves frontend/ directory |
| shutil (stdlib) | N/A | Copy SVGs to frontend/assets/ | Asset deployment step |

### Alternatives Considered
None -- this phase uses exclusively established project patterns. No new libraries needed.

**Installation:**
No new packages required. All dependencies are already in the project.

## Architecture Patterns

### Recommended Project Structure
```
frontend/
  assets/
    svg/
      mermaid.svg          # assembled defs+use SVG (already exists, ~768KB)
      dressup/             # NEW: individual variant SVGs for preview thumbnails
        tail-1.svg         # 66KB traced SVG
        tail-2.svg         # 109KB
        tail-3.svg         # 28KB
        hair-1.svg         # 99KB
        hair-2.svg         # 108KB
        hair-3.svg         # 34KB
        acc-1.svg          # 94KB
        acc-2.svg          # 89KB
        acc-3.svg          # 115KB
  js/
    dressup.js             # MODIFY: getVariantPreviewSVG, renderOptions
    app.js                 # MODIFY: asset path for mermaid.svg (relative)
  css/
    style.css              # MODIFY: option-btn sizing for 48x48 previews
src/mermaids/pipeline/
  assemble.py              # MODIFY: add copy_dressup_parts_to_frontend()
```

### Pattern 1: Fetched SVG Previews with Color Sync
**What:** Replace inline SVG preview strings with runtime-fetched actual traced SVGs, cached in a Map, with color override application.
**When to use:** When rendering the options-row for tail/hair/acc categories.
**Example:**
```javascript
// Cache for fetched preview SVGs (avoids re-fetching on tab switch)
const previewCache = new Map();

async function getVariantPreviewSVG(category, variantId) {
  if (previewCache.has(variantId)) {
    return previewCache.get(variantId);
  }
  try {
    const resp = await fetch(`assets/svg/dressup/${variantId}.svg`);
    const svgText = await resp.text();
    previewCache.set(variantId, svgText);
    return svgText;
  } catch {
    return ''; // graceful fallback
  }
}
```

### Pattern 2: Preview Color Sync
**What:** When a variant has a color override, modify the preview thumbnail SVG to reflect that color.
**When to use:** After recoloring a variant, update its preview button to show the applied color.
**Example:**
```javascript
function applyColorToPreviewSVG(svgElement, color) {
  // Same logic as applyColorToSource -- set fill on all paths/shapes
  const fillElements = svgElement.querySelectorAll('path, circle, ellipse, rect');
  fillElements.forEach(el => {
    const fill = el.getAttribute('fill');
    if (fill && fill !== 'none') {
      el.setAttribute('fill', color);
    }
  });
}
```

### Pattern 3: Background Path Handling
**What:** The first `<path>` in each traced SVG is a full-canvas background rectangle with fill="#FEFEFE". This should not be visible in the assembled SVG or previews.
**When to use:** During assembly and preview rendering.
**Example approach:** The assembly pipeline's `_make_variant_group()` already copies all child elements from the traced SVG. The background path gets the variant's scale transform applied (0.3906, 0.6836), which maps it to approximately 400x700 -- covering the viewBox. However, since it's inside `<defs>`, it only renders when referenced via `<use>`. The recolor function will also color this background path, which could cause the entire bounding box to fill with the chosen color.

**Mitigation options:**
1. Strip the first path (background rect) in `_make_variant_group()` during assembly
2. Set the first path to `fill="none"` during assembly
3. Filter it by checking if the path covers the full 1024x1024 bounding box

### Anti-Patterns to Avoid
- **Inlining 100KB+ SVGs in JavaScript strings:** The current getVariantPreviewSVG() returns inline strings. For 28-115KB traced SVGs, this would bloat the JS file. Fetch at runtime instead.
- **Re-fetching SVGs on every tab switch:** Cache fetched SVGs in a Map. The options-row is destroyed and recreated on each category tab click.
- **Modifying the preview cache SVG directly:** Clone the cached SVG text before applying color overrides, or apply colors to the DOM element after insertion.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SVG parsing for preview | Custom regex/string manipulation | DOMParser or innerHTML | SVG is XML; proper parsing handles edge cases |
| Asset file copying | Custom file copy logic | shutil.copy2 (already used) | Preserves timestamps, handles edge cases |
| Color application | Custom per-element-type logic | Existing getFillBearingElements() | Already tested, handles path/circle/ellipse/rect |

**Key insight:** Almost all the machinery for this phase already exists. The work is integration and adaptation, not new feature development.

## Common Pitfalls

### Pitfall 1: Background Rectangle in Traced SVGs
**What goes wrong:** The first `<path>` in every traced SVG is a full-canvas white background (fill="#FEFEFE"). When embedded in defs and recolored, this path fills the variant's entire bounding area with the selected color, obscuring the actual art.
**Why it happens:** vtracer traces the entire PNG including the white background, producing a path covering 0,0 to 1024,1024.
**How to avoid:** Strip or set fill="none" on the first path element during SVG assembly. The path has coordinates like "M0 0 C337.92 0 ... 0 0 Z" with fill="#FEFEFE".
**Warning signs:** Recoloring turns the entire variant area into a solid color block instead of coloring just the art shapes.

### Pitfall 2: Hundreds of Near-Identical Fill Colors
**What goes wrong:** Each traced SVG has hundreds of paths with slightly different hex colors (e.g., #765037, #775138, #764E37 -- all minor variations of brown). Uniform recoloring replaces ALL of them with one color, which is actually the desired behavior for kawaii flat-color style.
**Why it happens:** vtracer captures subtle color gradients from the AI-generated PNG.
**How to avoid:** This is actually fine for the use case -- uniform recolor matches the kawaii aesthetic. No special handling needed.
**Warning signs:** N/A (desired behavior).

### Pitfall 3: Async Preview Loading Causes Layout Shift
**What goes wrong:** Preview buttons render empty while SVGs are being fetched, then pop in, causing layout shift in the options row.
**Why it happens:** renderOptions() is currently synchronous; switching to async fetch means buttons appear before content.
**How to avoid:** Set fixed dimensions on option-btn (already 64x64 in CSS). Pre-fetch all previews on first dressup load, or show a placeholder during fetch.
**Warning signs:** Buttons jumping around or blank thumbnails flashing on tab switch.

### Pitfall 4: Large Preview SVGs Rendering Slowly at 48x48
**What goes wrong:** Traced SVGs with 500-900 paths render slowly when scaled down to 48x48 thumbnails, especially with 9+ previews visible simultaneously on iPad.
**Why it happens:** Browser must render hundreds of path elements even at tiny sizes.
**How to avoid:** Use viewBox on the `<svg>` element so the browser can optimize rendering. The traced SVGs already have width="1024" height="1024" -- set viewBox="0 0 1024 1024" and display at 48x48. Also consider lazy rendering or requestAnimationFrame for initial load.
**Warning signs:** Janky scrolling in options-row, delayed rendering after tab switch.

### Pitfall 5: Relative Asset Path for mermaid.svg Fetch
**What goes wrong:** `fetch("/assets/svg/mermaid.svg")` in app.js uses an absolute path that will break on GitHub Pages (Phase 7 requirement DPLY-02).
**Why it happens:** Currently using absolute path in renderDressUp().
**How to avoid:** Change to relative path: `fetch("assets/svg/mermaid.svg")`. This aligns with DPLY-02 requirement.
**Warning signs:** 404 errors when deployed to GitHub Pages subdirectory.

### Pitfall 6: Color State Not Reflected in Preview After Recolor
**What goes wrong:** User recolors tail-1 pink, switches to hair tab, switches back to tail tab -- tail-1 preview shows original colors instead of pink.
**Why it happens:** renderOptions() recreates buttons from cached (uncolored) SVG text. Needs to check state.colors and apply override after inserting into DOM.
**How to avoid:** After inserting preview SVG into button, check `state.colors[variantId]` and apply color if set.
**Warning signs:** Preview thumbnails don't match the mermaid on screen.

## Code Examples

### Rewriting getVariantPreviewSVG to Async Fetch
```javascript
// Source: Project codebase analysis

// Preview SVG text cache (persists across tab switches)
const previewSVGCache = new Map();

async function fetchVariantPreview(variantId) {
  if (previewSVGCache.has(variantId)) {
    return previewSVGCache.get(variantId);
  }
  const resp = await fetch(`assets/svg/dressup/${variantId}.svg`);
  const text = await resp.text();
  previewSVGCache.set(variantId, text);
  return text;
}
```

### Async renderOptions with Color Sync
```javascript
// Source: Project codebase analysis

async function renderOptions(category) {
  const row = document.getElementById("options-row");
  if (!row) return;
  row.innerHTML = "";

  if (category === "color") {
    // ... existing color swatch logic unchanged ...
    return;
  }

  const variants = PARTS[category];
  if (!variants) return;

  for (const variantId of variants) {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.setAttribute("data-variant", variantId);
    btn.setAttribute("aria-label", variantId);

    if (state[category] === variantId) {
      btn.classList.add("selected");
    }

    // Fetch and insert preview SVG
    const svgText = await fetchVariantPreview(variantId);
    btn.innerHTML = svgText;

    // Set viewBox for proper scaling in 48x48 display
    const svgEl = btn.querySelector("svg");
    if (svgEl) {
      svgEl.setAttribute("width", "48");
      svgEl.setAttribute("height", "48");
      if (!svgEl.getAttribute("viewBox")) {
        svgEl.setAttribute("viewBox", "0 0 1024 1024");
      }
    }

    // Apply color override if one exists
    const savedColor = state.colors[variantId];
    if (savedColor && svgEl) {
      applyColorToPreviewSVG(svgEl, savedColor);
    }

    btn.addEventListener("click", () => {
      swapPart(category, variantId);
      row.querySelectorAll(".option-btn").forEach((b) => {
        b.classList.toggle("selected", b.getAttribute("data-variant") === variantId);
      });
    });
    row.appendChild(btn);
  }
}
```

### Copy Dressup Parts to Frontend (Python)
```python
# Source: Pattern from existing copy_coloring_pages_to_frontend()

def copy_dressup_parts_to_frontend() -> list[Path]:
    """Copy traced dressup variant SVGs to frontend/assets/svg/dressup/."""
    src_dir = GENERATED_SVG_DIR / "dressup"
    dst_dir = FRONTEND_SVG_DIR / "dressup"
    dst_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if not src_dir.exists():
        return results

    for svg_file in sorted(src_dir.glob("*.svg")):
        dst = dst_dir / svg_file.name
        shutil.copy2(svg_file, dst)
        results.append(dst)

    return results
```

### CSS Adjustments for 48x48 Preview SVGs
```css
/* Source: Project CSS analysis -- option-btn is already 64x64,
   inner SVG needs sizing constraints */

.option-btn svg {
    width: 48px;
    height: 48px;
    max-width: 48px;
    max-height: 48px;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-crafted inline SVG previews | Fetched traced SVG previews | Phase 6 | Preview thumbnails show actual AI art |
| 24x24 preview icons | 48x48 preview SVGs in 64x64 buttons | Phase 6 | Meets 60pt+ touch target guideline |
| Hardcoded mermaid.svg | Assembled from traced AI art | Phase 4 (exists) | Already done -- just needs frontend deployment |
| Absolute asset path `/assets/svg/` | Relative path `assets/svg/` | Phase 6 | Prepares for GitHub Pages (DPLY-02) |

**Deprecated/outdated:**
- Inline getVariantPreviewSVG() with hardcoded SVG strings: replaced by async fetch
- 24x24 viewBox preview icons: replaced by 48x48 actual art thumbnails

## Open Questions

1. **Background path in traced SVGs -- strip or hide?**
   - What we know: First path in each traced SVG is a white background covering 1024x1024
   - What's unclear: Whether to strip it in assemble.py or handle it in the frontend
   - Recommendation: Strip in assemble.py during `_make_variant_group()` -- cleaner, one-time fix

2. **Body/face visual cohesion with AI-generated parts**
   - What we know: Body and face are hardcoded in assemble.py with specific skin tone (#f5c8a8) and geometric shapes
   - What's unclear: Whether hardcoded body/face looks visually coherent next to kawaii AI-generated parts
   - Recommendation: Evaluate visually first. If mismatch is obvious, regenerate body art using the same AI pipeline. Per CONTEXT.md, this is Claude's Discretion and extra API calls are OK.

3. **Preview SVG file sizes and performance**
   - What we know: Individual SVGs range 28KB-115KB with 22-926 paths each
   - What's unclear: Whether rendering 3-4 of these simultaneously as 48x48 thumbnails causes iPad performance issues
   - Recommendation: Test on actual hardware. If slow, consider pre-rendering thumbnails as smaller PNGs or simplified SVGs as a follow-up optimization.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8+ with playwright 1.49+ |
| Config file | pyproject.toml [tool.pytest.ini_options] |
| Quick run command | `uv run pytest tests/test_dressup.py -x` |
| Full suite command | `uv run pytest tests/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DRSV-01 | Dress-up screen displays AI-generated kawaii mermaid | e2e | `uv run pytest tests/test_dressup.py::TestDressUpView -x` | Exists (needs update for AI art verification) |
| DRSV-02 | Tapping variant swaps mermaid part via defs+use | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping -x` | Exists (should still pass with new art) |
| DRSV-03 | Tapping color swatch recolors selected part | e2e | `uv run pytest tests/test_dressup.py::TestColorRecolor -x` | Exists (should still pass with new art) |
| DRSV-01 | Preview thumbnails use actual traced SVGs | e2e | `uv run pytest tests/test_dressup.py::TestPreviewThumbnails -x` | Does not exist -- Wave 0 |
| DRSV-01 | Preview thumbnails reflect color overrides | e2e | `uv run pytest tests/test_dressup.py::TestPreviewColorSync -x` | Does not exist -- Wave 0 |
| DRSV-01 | Individual variant SVGs served from /assets/svg/dressup/ | unit | `uv run pytest tests/test_assemble.py::TestCopyDressupParts -x` | Does not exist -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_dressup.py -x`
- **Per wave merge:** `uv run pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_dressup.py::TestPreviewThumbnails` -- verify preview buttons contain fetched SVGs (not inline hardcoded)
- [ ] `tests/test_dressup.py::TestPreviewColorSync` -- verify preview reflects color override after recolor
- [ ] `tests/test_assemble.py::TestCopyDressupParts` -- verify copy_dressup_parts_to_frontend() deploys 9 SVGs
- [ ] Update `tests/test_dressup.py::TestDressUpView` to verify AI art present (e.g., check path count > 100 inside variant defs)

## Sources

### Primary (HIGH confidence)
- Project codebase: `frontend/js/dressup.js` -- current variant swap and recolor implementation
- Project codebase: `frontend/js/app.js` -- renderDressUp() fetch and SVG loading
- Project codebase: `src/mermaids/pipeline/assemble.py` -- SVG assembly with defs+use structure
- Project codebase: `frontend/css/style.css` -- option-btn sizing (64x64), color-swatch sizing (52x52)
- Project codebase: `assets/generated/svg/dressup/*.svg` -- 9 traced variant SVGs (analyzed fill patterns)
- Project codebase: `tests/test_dressup.py` -- existing Playwright e2e tests
- Project codebase: `tests/test_assemble.py` -- existing assembly unit tests

### Secondary (MEDIUM confidence)
- SVG specification: `<defs>` + `<use>` href mechanism for variant referencing
- vtracer output characteristics: full-canvas background path, hundreds of paths per traced SVG

### Tertiary (LOW confidence)
- iPad Safari rendering performance with 500+ path SVG thumbnails at 48x48 (needs real device testing)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - entirely existing project patterns, no new dependencies
- Architecture: HIGH - extension of proven defs+use mechanism, well-understood codebase
- Pitfalls: HIGH - identified from direct analysis of traced SVG files and existing code
- Validation: HIGH - existing test infrastructure covers most requirements, gaps identified

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable -- no external dependencies changing)
