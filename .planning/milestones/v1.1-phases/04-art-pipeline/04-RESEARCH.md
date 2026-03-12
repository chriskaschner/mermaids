# Phase 4: Art Pipeline - Research

**Researched:** 2026-03-09
**Domain:** AI image generation (OpenAI gpt-image-1), raster-to-vector tracing (vtracer), SVG asset pipeline
**Confidence:** MEDIUM

## Summary

Phase 4 is a local Python script pipeline that generates kawaii mermaid art via the OpenAI gpt-image-1 API, traces raster PNGs to clean SVGs via vtracer, and produces dress-up part variants using the edit API with masks. The output replaces existing hand-crafted SVG assets in `frontend/assets/svg/`.

The existing codebase already has `trace.py` with vtracer integration, Pillow in dependencies, and a well-structured SVG defs+use pattern in `mermaid.svg`. The main new work is: (1) adding the OpenAI SDK, (2) writing generation scripts with good prompts, (3) creating mask images for the edit API, and (4) assembling traced SVGs into the defs+use format that `dressup.js` expects.

**Primary recommendation:** Use `openai>=2.0` Python SDK with `client.images.generate()` for coloring pages and `client.images.edit()` with RGBA PNG masks for dress-up variants. Keep separate scripts per pipeline stage (generate, trace, assemble) with a thin orchestrator. Extend the existing `trace.py` for the tracing step.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Chibi kawaii style: big head, small body, oversized eyes, minimal detail (Sanrio-like)
- Coloring pages: generate black-and-white outline art directly (not full-color traced to outlines)
- Dress-up parts: generate full-color with flat fills for easy recoloring via fill attribute swaps
- Cross-generation consistency is not critical -- minor style variation between pages/parts is acceptable
- No need for seed-based anchoring or manual curation workflow
- 4 coloring pages replacing existing (ocean, castle, seahorse, coral themes in chibi kawaii style)
- 3 tails, 3 hair styles, 3 accessories (matching current v1.0 variant count)
- OPENAI_API_KEY environment variable (standard Python pattern)
- Keep generated PNGs in a separate directory (e.g., assets/generated/png/) for debugging and re-tracing
- Only final SVGs go to frontend/assets/svg/
- Auto-retry failed API calls 3 times with exponential backoff
- Skip already-generated assets on re-run (idempotent)
- trace.py already exists in src/mermaids/pipeline/

### Claude's Discretion
- Approach for spatial alignment of dress-up parts (base mermaid + edit API masks vs separate generation). Pick whatever is most reliable with gpt-image-1.
- defs+use pattern vs separate SVG files per part. Pick what works best with vtracer output and existing frontend code (dressup.js uses setAttribute to swap `<use>` href).
- One orchestrator script vs separate scripts per stage. Pick what works best for a dev-facing tool with retry and re-run needs.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ARTP-01 | Local script generates kawaii mermaid coloring page PNGs via OpenAI gpt-image-1 API | OpenAI SDK `client.images.generate()` with b64_json response, Pillow for saving. Prompts for B&W outline chibi kawaii art. |
| ARTP-02 | Local script traces generated PNGs to SVG via vtracer | Existing `trace.py` with `trace_to_svg()` handles this. Use `simplify=True` (binary mode) for coloring pages, `simplify=False` (color mode) for dress-up parts. |
| ARTP-03 | Local script generates dress-up mermaid variant parts (tails, hair, accessories) with consistent alignment via edit API masks | `client.images.edit()` with RGBA PNG masks. Generate base mermaid first, then use masks to regenerate specific regions (tail zone, hair zone, accessory zone). |
| ARTP-04 | Generated SVG assets are committed to frontend/assets/svg/ for static serving | Coloring pages replace files in `frontend/assets/svg/coloring/`. Dress-up parts assembled into single `mermaid.svg` with defs+use pattern matching existing structure. |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | >=2.0 | OpenAI API client for gpt-image-1 generation and editing | Official Python SDK, typed responses, async support |
| vtracer | >=0.6.12 | Raster-to-SVG tracing | Already in project dependencies, handles binary and color modes |
| Pillow | >=11 | Image manipulation (resize, mask creation, format conversion) | Already in project dependencies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| base64 | stdlib | Decode b64_json responses from OpenAI API | Every image generation/edit call |
| pathlib | stdlib | File path management | Throughout pipeline |
| xml.etree.ElementTree | stdlib | SVG XML manipulation for assembling defs+use structure | Assembling final mermaid.svg |
| time | stdlib | Exponential backoff for retries | API error handling |
| io.BytesIO | stdlib | In-memory image buffers for mask creation | Mask preparation for edit API |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| gpt-image-1 | gpt-image-1.5 | 1.5 is faster (10-30s vs 30-60s) and has better edit consistency, but user locked decision to gpt-image-1 in STATE.md. If budget allows, 1.5 is strictly better. |
| vtracer binary mode | potrace | potrace is more battle-tested for B&W tracing but vtracer is already integrated and works well |
| xml.etree.ElementTree | lxml | lxml has better SVG namespace handling but adds a dependency for minimal benefit here |

**Installation:**
```bash
uv add openai
```

Note: vtracer and Pillow are already in `pyproject.toml` dependencies. The openai package is the only new dependency.

## Architecture Patterns

### Recommended Project Structure
```
src/mermaids/pipeline/
    __init__.py          # existing
    trace.py             # existing - vtracer wrapper
    generate.py          # NEW - OpenAI image generation (coloring pages)
    edit.py              # NEW - OpenAI image editing with masks (dress-up parts)
    assemble.py          # NEW - SVG assembly (combine traced parts into defs+use)
    prompts.py           # NEW - prompt templates for kawaii style
    config.py            # NEW - shared constants (sizes, paths, retry config)

assets/generated/
    png/
        coloring/        # raw PNGs from generation API
        dressup/
            base/        # base mermaid PNG
            masks/        # RGBA mask PNGs for each region
            parts/       # edited part PNGs
    svg/
        coloring/        # traced coloring page SVGs (intermediate)
        dressup/         # traced dress-up part SVGs (intermediate)

scripts/
    generate_coloring.py   # CLI entry: generate coloring page PNGs
    generate_dressup.py    # CLI entry: generate dress-up part PNGs via edit API
    trace_all.py           # CLI entry: trace all PNGs to SVGs
    assemble_mermaid.py    # CLI entry: assemble parts into mermaid.svg
    run_pipeline.py        # CLI entry: orchestrate all stages
```

### Pattern 1: Idempotent Generation with Skip Logic
**What:** Each script checks for existing output before making API calls. Re-running skips completed work.
**When to use:** Every generation and tracing step.
**Example:**
```python
from pathlib import Path

def generate_if_missing(output_path: Path, generate_fn, *args, **kwargs):
    """Skip generation if output already exists."""
    if output_path.exists():
        print(f"  Skipping (exists): {output_path}")
        return output_path
    print(f"  Generating: {output_path}")
    return generate_fn(output_path, *args, **kwargs)
```

### Pattern 2: Retry with Exponential Backoff
**What:** Wrap API calls with retry logic for transient failures (rate limits, server errors).
**When to use:** Every OpenAI API call.
**Example:**
```python
import time
from openai import RateLimitError, APIError

def retry_api_call(fn, max_retries=3, base_delay=2.0):
    """Retry an API call with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except (RateLimitError, APIError) as e:
            if attempt == max_retries:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"  Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
            time.sleep(delay)
```

### Pattern 3: Base Mermaid + Mask Editing for Dress-Up Parts
**What:** Generate a single base mermaid image, then use the edit API with region-specific masks to generate variant parts while preserving the base anatomy.
**When to use:** Dress-up part generation (ARTP-03).
**Example:**
```python
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64

client = OpenAI()  # uses OPENAI_API_KEY env var

def create_region_mask(base_size: tuple, region_bbox: tuple) -> bytes:
    """Create RGBA mask PNG with transparent region where editing should occur.

    Transparent pixels = area to replace.
    Opaque pixels = area to preserve.
    """
    mask = Image.new("RGBA", base_size, (0, 0, 0, 255))  # fully opaque
    # Make the target region transparent
    for x in range(region_bbox[0], region_bbox[2]):
        for y in range(region_bbox[1], region_bbox[3]):
            mask.putpixel((x, y), (0, 0, 0, 0))  # transparent

    buf = BytesIO()
    mask.save(buf, format="PNG")
    return buf.getvalue()

def edit_region(base_image_path: str, mask_bytes: bytes, prompt: str) -> bytes:
    """Edit a region of the base image using the mask."""
    result = client.images.edit(
        model="gpt-image-1",
        image=open(base_image_path, "rb"),
        mask=BytesIO(mask_bytes),
        prompt=prompt,
        size="1024x1024",
    )
    return base64.b64decode(result.data[0].b64_json)
```

### Pattern 4: SVG Assembly with defs+use
**What:** Parse traced SVG parts, extract path data, wrap in `<g id="part-N">` groups, and combine into a single SVG with `<defs>` and `<use>` elements matching the existing mermaid.svg structure.
**When to use:** Final assembly step (ARTP-04).
**Example:**
```python
import xml.etree.ElementTree as ET

def assemble_mermaid_svg(parts: dict, template_path: str, output_path: str):
    """Assemble traced parts into defs+use SVG structure.

    parts: {"tail-1": "path/to/tail-1.svg", "tail-2": ..., "hair-1": ...}
    """
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    # Build SVG with same viewBox as existing (400x700)
    root = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": "0 0 400 700",
        "preserveAspectRatio": "xMidYMid meet",
        "id": "mermaid-svg",
    })
    defs = ET.SubElement(root, "defs")

    for part_id, svg_path in parts.items():
        part_tree = ET.parse(svg_path)
        part_root = part_tree.getroot()
        g = ET.SubElement(defs, "g", {"id": part_id})
        # Copy all child elements from traced SVG into the group
        for child in part_root:
            g.append(child)

    # ... add body, use elements, face details
```

### Anti-Patterns to Avoid
- **Generating full-color images and tracing to outlines for coloring pages:** The user explicitly decided to generate B&W outline art directly. Tracing full-color images to outlines produces messier results.
- **Generating all parts independently without a base image:** Parts will not align spatially. Use the edit API with masks on a shared base mermaid for dress-up parts.
- **Hardcoding prompts inline:** Extract prompt templates to a separate module for easy iteration without touching pipeline logic.
- **Making the pipeline a single monolithic script:** Separate stages allow re-running just the failing step without repeating expensive API calls.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Raster to SVG conversion | Custom edge detection + path tracing | vtracer `convert_image_to_svg_py()` | Thousands of edge cases in vectorization. vtracer handles speckle filtering, curve fitting, hierarchical tracing. |
| HTTP retry logic with backoff | Custom retry loop from scratch | `tenacity` or simple wrapper around OpenAI's built-in retry | OpenAI SDK v2 has some built-in retry for rate limits. Supplement with explicit retry wrapper for other transient errors. |
| SVG path optimization | Manual path simplification | vtracer's `filter_speckle` + `path_precision` params | Already tuned in existing trace.py |
| Mask image creation | Manual pixel manipulation | Pillow `Image.new("RGBA")` + `putalpha()` | Standard approach documented in OpenAI cookbook |

**Key insight:** The pipeline is glue code connecting OpenAI API and vtracer. The hard problems (image generation, vectorization) are solved by these tools. Focus pipeline code on prompt engineering, file management, and SVG assembly.

## Common Pitfalls

### Pitfall 1: Mask Dimensions Must Match Image Exactly
**What goes wrong:** Edit API rejects the request or produces garbled output.
**Why it happens:** The mask PNG must have identical pixel dimensions to the input image.
**How to avoid:** Always create masks from the base image dimensions: `mask = Image.new("RGBA", base_image.size, ...)`.
**Warning signs:** API error "mask must have the same dimensions as the image."

### Pitfall 2: Mask Transparency Semantics Are Inverted from Intuition
**What goes wrong:** The preserved region gets edited and the edit region stays unchanged.
**Why it happens:** In OpenAI's mask format, transparent pixels mark the area TO BE REPLACED. Opaque pixels mark the area to PRESERVE. This is the opposite of what many developers expect.
**How to avoid:** Always verify: transparent = edit here, opaque = keep this.
**Warning signs:** Generated parts appear outside the intended region.

### Pitfall 3: vtracer Color Mode Produces Filled Shapes, Not Outlines
**What goes wrong:** Coloring pages have filled colored regions instead of clean line art.
**Why it happens:** Using `colormode="color"` on B&W line art produces filled black shapes instead of stroked outlines.
**How to avoid:** For coloring pages, generate B&W outline art and trace with `simplify=True` (binary mode). For dress-up parts, use `simplify=False` (color mode) to preserve flat color fills.
**Warning signs:** SVG has large filled `<path>` elements instead of thin stroked outlines.

### Pitfall 4: SVG Coordinate Space Mismatch
**What goes wrong:** Traced SVG parts don't align when assembled into the composite mermaid.svg.
**Why it happens:** vtracer outputs SVG with viewBox matching the input image dimensions (e.g., 1024x1024). The existing mermaid.svg uses viewBox="0 0 400 700". Parts need coordinate transformation.
**How to avoid:** Either (a) generate images at the target aspect ratio and scale SVG viewBox, or (b) use SVG `transform="translate(...) scale(...)"` on each group, or (c) resize/crop input images to match the target coordinate system before tracing.
**Warning signs:** Parts appear tiny, huge, or offset when rendered in the composite SVG.

### Pitfall 5: gpt-image-1 Ignores Exact Mask Boundaries
**What goes wrong:** Edits bleed outside the masked region or don't fill it completely.
**Why it happens:** Unlike DALL-E 2, gpt-image-1 treats masks as "guidance" rather than strict boundaries. The model uses the mask as a hint but may paint slightly outside it.
**How to avoid:** Accept slight bleed as normal. Use generous mask regions. Post-process traced SVGs to clip to expected bounding boxes if needed. Prompt clearly about what should be in the edited region.
**Warning signs:** Generated parts have artifacts at mask boundaries.

### Pitfall 6: OpenAI API Rate Limits on Image Generation
**What goes wrong:** Pipeline fails mid-way through batch generation.
**Why it happens:** Image generation endpoints have lower rate limits than text endpoints. Generating 4 coloring pages + 1 base + 9 variants = 14 API calls, which may hit rate limits.
**How to avoid:** Implement exponential backoff retry (already decided). Add small delays between sequential calls (0.5-1s). The idempotent skip logic ensures re-runs pick up where they left off.
**Warning signs:** HTTP 429 responses from OpenAI.

### Pitfall 7: Large SVG Files from Color Tracing
**What goes wrong:** Dress-up part SVGs are hundreds of KB, slow to load on iPad.
**Why it happens:** Color mode tracing with AI-generated images produces many paths (gradients, anti-aliasing artifacts become separate shapes).
**How to avoid:** Tune vtracer params: increase `filter_speckle` (20-40), reduce `color_precision` (3-4), increase `layer_difference` (48-64). For flat-color fills, these aggressive settings work well. The existing trace.py already has good defaults.
**Warning signs:** SVG file sizes > 100KB per part, or slow rendering in browser.

## Code Examples

### Coloring Page Generation (ARTP-01)
```python
# Source: OpenAI cookbook + project CONTEXT.md
from openai import OpenAI
from pathlib import Path
import base64

client = OpenAI()  # OPENAI_API_KEY env var

COLORING_PAGES = [
    {"id": "page-1-ocean", "prompt_detail": "swimming in the ocean with small fish and bubbles around her"},
    {"id": "page-2-castle", "prompt_detail": "sitting on a rock near an underwater castle with towers and arches"},
    {"id": "page-3-seahorse", "prompt_detail": "riding a cute seahorse friend with seaweed in the background"},
    {"id": "page-4-coral", "prompt_detail": "playing among coral reef formations with starfish on the ground"},
]

BASE_PROMPT = (
    "Black and white coloring page outline art. Clean simple lines on white background. "
    "Chibi kawaii mermaid character with big head, small body, oversized round eyes, "
    "minimal detail, Sanrio-like cute style. "
    "No shading, no gradients, no fills -- only clean black outlines suitable for a child to color in. "
)

def generate_coloring_page(page: dict, output_dir: Path) -> Path:
    output_path = output_dir / f"{page['id']}.png"
    if output_path.exists():
        print(f"  Skipping (exists): {output_path}")
        return output_path

    prompt = BASE_PROMPT + page["prompt_detail"]
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="high",
    )
    image_bytes = base64.b64decode(result.data[0].b64_json)
    output_path.write_bytes(image_bytes)
    return output_path
```

### Mask Creation for Dress-Up Parts (ARTP-03)
```python
# Source: OpenAI cookbook mask format documentation
from PIL import Image
from io import BytesIO

# Region definitions matching mermaid.svg viewBox (400x700)
# Mapped to 1024x1024 generation space
REGIONS = {
    "tail": (256, 500, 768, 1024),   # x1, y1, x2, y2 in 1024x1024 space
    "hair": (256, 0, 768, 300),
    "acc":  (350, 0, 700, 200),
}

def create_mask(image_size: tuple, region: tuple) -> bytes:
    """Create RGBA mask: transparent where we want edits, opaque elsewhere."""
    mask = Image.new("RGBA", image_size, (0, 0, 0, 255))
    pixels = mask.load()
    x1, y1, x2, y2 = region
    for y in range(y1, min(y2, image_size[1])):
        for x in range(x1, min(x2, image_size[0])):
            pixels[x, y] = (0, 0, 0, 0)  # transparent = edit here
    buf = BytesIO()
    mask.save(buf, format="PNG")
    return buf.getvalue()
```

### Tracing with Existing trace.py (ARTP-02)
```python
# Source: existing src/mermaids/pipeline/trace.py
from mermaids.pipeline.trace import trace_to_svg

# Coloring pages: binary mode for clean outlines
trace_to_svg("assets/generated/png/coloring/page-1-ocean.png",
             "assets/generated/svg/coloring/page-1-ocean.svg",
             simplify=True)

# Dress-up parts: color mode for flat fills
trace_to_svg("assets/generated/png/dressup/parts/tail-1.png",
             "assets/generated/svg/dressup/tail-1.svg",
             simplify=False)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DALL-E 3 for image generation | gpt-image-1 (or gpt-image-1.5) | April 2025 | Better instruction following, native multimodal, better text rendering |
| DALL-E 2 edit API (strict masks) | gpt-image-1 edit API (guidance-based masks) | April 2025 | Masks are guidance not boundaries; more natural edits but less precise |
| openai Python SDK v1.x | openai Python SDK v2.x | Late 2025 | Drops Python 3.9 support, otherwise similar images API |
| response_format="url" (default) | b64_json is more reliable for scripts | Ongoing | URLs expire; b64_json is immediately available, no download step |

**Deprecated/outdated:**
- DALL-E 2 and DALL-E 3: removed from API on May 12, 2026. Use gpt-image-1.
- `openai.Image.create()` (old SDK style): Use `client.images.generate()` (v1.x+/v2.x style).

## Discretion Recommendations

### Dress-Up Part Alignment: Base Mermaid + Edit API Masks (RECOMMENDED)
**Reasoning:** The edit API preserves the unmasked regions, ensuring body/face remain identical across all variants. Generating parts separately would produce different body shapes and proportions each time. The mask-based approach is the whole point of the edit API.

**Approach:**
1. Generate one "base mermaid" image with default tail, hair, no accessories
2. Create 3 mask images per category (tail region, hair region, accessory region)
3. For each variant, call `images.edit()` with the base image + region mask + variant prompt
4. Extract just the edited region from the result for tracing

### SVG Structure: Single mermaid.svg with defs+use (RECOMMENDED)
**Reasoning:** The existing `dressup.js` code uses `getElementById("active-tail")`, `setAttribute("href", "#tail-1")` etc. It expects all variants in `<defs>` with `<use>` references. Changing to separate SVG files would require rewriting the frontend JS. Keep the same pattern.

**Approach:**
1. Trace each dress-up part variant to its own intermediate SVG
2. Parse each SVG, extract path/shape elements
3. Wrap in `<g id="tail-1">`, `<g id="hair-2">` etc.
4. Combine all groups into `<defs>` section of mermaid.svg
5. Keep the existing `<use>`, body group, and face detail structure

### Script Design: Separate Scripts with Thin Orchestrator (RECOMMENDED)
**Reasoning:** With idempotent skip logic and retry needs, separate scripts let developers re-run just the failing stage. A thin orchestrator calls them in sequence for full pipeline runs.

**Approach:**
- `generate_coloring.py` -- generate coloring page PNGs (ARTP-01)
- `generate_dressup.py` -- generate base mermaid + edit variants (ARTP-03)
- `trace_all.py` -- trace all PNGs to SVGs (ARTP-02)
- `assemble_mermaid.py` -- assemble dress-up SVGs into mermaid.svg (ARTP-04)
- `run_pipeline.py` -- call all above in sequence

## Open Questions

1. **Exact mask region coordinates for dress-up parts**
   - What we know: The existing mermaid.svg uses viewBox="0 0 400 700" with tail at y=340-670, hair at y=20-150, accessories at y=20-60
   - What's unclear: What mask coordinates to use in 1024x1024 generation space to produce parts that align after tracing and scaling
   - Recommendation: Start with proportional mapping from 400x700 to 1024x1024 (or use 1024x1536 portrait for better aspect ratio match). Iterate on mask bounds based on generation results. This is inherently iterative.

2. **vtracer parameter tuning for AI-generated images**
   - What we know: Existing trace.py params work for hand-drawn/simple images. AI-generated images have different detail levels (soft gradients, anti-aliasing).
   - What's unclear: Whether current `filter_speckle=20`, `color_precision=4` settings produce clean enough output for AI art.
   - Recommendation: Start with existing params, visually inspect results, tune if needed. The `filter_speckle` and `layer_difference` params are the main knobs.

3. **Coloring page SVG structure for Phase 5 flood fill**
   - What we know: Current coloring pages use `<g data-region="...">` groups for tap-to-fill. Phase 5 switches to canvas-based flood fill which does not need SVG regions.
   - What's unclear: Whether traced SVGs need any special structure for Phase 5, or if raw traced outlines are sufficient.
   - Recommendation: For now, produce clean traced SVGs without region annotations. Phase 5 (canvas flood fill) works by pixel color matching, not SVG regions. The SVG overlay just needs clean outlines.

4. **Cost estimation for full pipeline run**
   - What we know: ~$0.07/medium quality image, ~$0.19/high quality. 4 coloring pages + 1 base mermaid + 9 variants = 14 images.
   - What's unclear: Exact cost depends on quality setting and retries.
   - Recommendation: Use "high" quality for the 4 coloring pages (visible to end user), "medium" for dress-up parts (will be traced anyway). Estimated cost: ~$1.40 per full pipeline run.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >= 8 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/test_pipeline.py -x` |
| Full suite command | `uv run pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARTP-01 | Generate coloring page PNGs via OpenAI API | unit (mocked API) | `uv run pytest tests/test_generate.py::test_coloring_generation -x` | Wave 0 |
| ARTP-01 | Skip existing files on re-run | unit | `uv run pytest tests/test_generate.py::test_idempotent_skip -x` | Wave 0 |
| ARTP-01 | Retry on API errors with backoff | unit (mocked) | `uv run pytest tests/test_generate.py::test_retry_backoff -x` | Wave 0 |
| ARTP-02 | Trace PNGs to SVGs via vtracer | unit | `uv run pytest tests/test_pipeline.py::test_trace_produces_valid_svg -x` | Exists |
| ARTP-02 | Binary mode produces clean outlines | unit | `uv run pytest tests/test_pipeline.py::test_simplify_produces_fewer_paths -x` | Exists |
| ARTP-03 | Create RGBA mask PNGs with correct transparency | unit | `uv run pytest tests/test_masks.py::test_mask_transparency -x` | Wave 0 |
| ARTP-03 | Edit API generates variant parts | unit (mocked API) | `uv run pytest tests/test_generate.py::test_dressup_edit -x` | Wave 0 |
| ARTP-04 | Assembled SVG has correct defs+use structure | unit | `uv run pytest tests/test_assemble.py::test_defs_use_structure -x` | Wave 0 |
| ARTP-04 | Assembled SVG has all expected variant IDs | unit | `uv run pytest tests/test_assemble.py::test_variant_ids -x` | Wave 0 |
| ARTP-04 | Final SVGs exist in frontend/assets/svg/ | smoke | `uv run pytest tests/test_assemble.py::test_output_paths -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_pipeline.py tests/test_generate.py tests/test_masks.py tests/test_assemble.py -x`
- **Per wave merge:** `uv run pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_generate.py` -- covers ARTP-01, ARTP-03 (mocked OpenAI API calls)
- [ ] `tests/test_masks.py` -- covers ARTP-03 (mask creation, RGBA format verification)
- [ ] `tests/test_assemble.py` -- covers ARTP-04 (SVG assembly, defs+use structure)
- [ ] OpenAI SDK mock fixtures in conftest.py or test_generate.py

## Sources

### Primary (HIGH confidence)
- OpenAI Cookbook: Generate images with GPT Image (https://developers.openai.com/cookbook/examples/generate_images_with_gpt_image/) -- generation and edit API examples, parameter reference
- OpenAI API Deprecations (https://developers.openai.com/api/docs/deprecations/) -- DALL-E deprecation timeline, gpt-image-1 as replacement
- Existing project code: `src/mermaids/pipeline/trace.py`, `frontend/assets/svg/mermaid.svg`, `frontend/js/dressup.js`
- vtracer PyPI (https://pypi.org/project/vtracer/) -- parameter reference for convert_image_to_svg_py
- OpenAI Python SDK PyPI (https://pypi.org/project/openai/) -- current version v2.26.0

### Secondary (MEDIUM confidence)
- OpenAI Community Forum: transparent backgrounds with edit API (https://community.openai.com/t/gpt-image-1-transparent-backgrounds-with-edit-request/1240577) -- mask semantics, background parameter
- Analytics Vidhya: gpt-image-1 editing guide (https://www.analyticsvidhya.com/blog/2025/04/openai-gpt-image-1/) -- mask format requirements, code examples
- Cohorte: mastering image generation API (https://www.cohorte.co/blog/mastering-openais-new-image-generation-api-a-developers-guide) -- parameters, pricing

### Tertiary (LOW confidence)
- gpt-image-1.5 existence and capabilities -- mentioned in search results but not verified against official deprecation/model pages. User decision specifies gpt-image-1 so this is informational only.
- Exact mask boundary behavior with gpt-image-1 -- community reports suggest guidance-based rather than strict, but exact behavior requires testing.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- OpenAI SDK and vtracer are well-documented, already partially integrated
- Architecture: MEDIUM -- pipeline structure is sound but mask regions and vtracer tuning need iteration
- Pitfalls: HIGH -- mask format, coordinate space, and rate limit issues are well-documented in community
- Code examples: MEDIUM -- generation examples verified against cookbook, assembly code is extrapolated from existing mermaid.svg structure

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable domain, OpenAI API is mature)
