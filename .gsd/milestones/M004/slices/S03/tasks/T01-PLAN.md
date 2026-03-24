---
estimated_steps: 5
estimated_files: 7
skills_used:
  - test
---

# T01: Write content-quality test and generate placeholder coloring SVGs for pages 5-9

**Slice:** S03 — Coloring Page Art Fix
**Milestone:** M004

## Description

Pages 5-9 of the coloring gallery are 170-byte empty vtracer stubs (width="1" height="1", zero `<path` elements). No OpenAI API key is available, so we create scene-themed geometric placeholder SVGs using the same pattern established by `scripts/generate_dressup_outlines.py --placeholder`. A content-quality test in the existing test file locks the invariant that all 9 gallery SVGs contain real art.

The 5 scenes are: forest (kelp forest), treasure (treasure chest), jellyfish (jellyfish meadow), whirlpool (whirlpool vortex), starfish (starfish beach). Each SVG is 1024x1024, B&W outlines only (white fill, black stroke), containing a mermaid figure plus scene-specific elements. Each must have ≥8 `<path` elements to pass the ≥5 threshold with margin.

## Steps

1. **Add content-quality test** to `tests/test_trace_coloring.py` in the existing `TestColoringSVGAssets` class:
   ```python
   def test_all_coloring_svgs_have_real_art(self):
       """All 9 coloring SVGs contain >= 5 <path elements (real art, not 1x1 placeholder)."""
       svg_dir = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "svg" / "coloring"
       failing = []
       for svg_file in sorted(svg_dir.glob("page-*.svg")):
           content = svg_file.read_text(encoding="utf-8")
           path_count = content.count("<path")
           if path_count < 5:
               failing.append(f"{svg_file.name}: {path_count} paths")
       assert not failing, f"SVGs with insufficient paths (real art needs >= 5): {failing}"
   ```
   Run the test — it should FAIL for pages 5-9 (0 paths each). This confirms the test catches the problem.

2. **Create `scripts/generate_coloring_placeholders.py`** — a standalone script that generates 5 geometric placeholder SVGs for pages 5-9. Use the same SVG structure pattern as `scripts/generate_dressup_outlines.py` `_build_placeholder_svg()`: 1024x1024 viewBox, white background rect, black-stroked paths with white fill. Each scene needs:
   - A mermaid figure (head ellipse, eyes, body torso, hair, tail, fins — reuse the basic body template from the dressup placeholders)
   - Scene-specific elements (5+ unique `<path` or shape elements per scene):
     - **page-5-forest**: tall kelp/seaweed stalks, bubbles
     - **page-6-treasure**: treasure chest on ocean floor, coins/gems
     - **page-7-jellyfish**: 2-3 jellyfish shapes with tentacles
     - **page-8-whirlpool**: spiral/vortex paths, swirling bubbles
     - **page-9-starfish**: starfish shapes, sand dollars, beach elements
   - Total `<path` count per SVG: ≥8 (mermaid body paths + scene paths)

3. **Run the placeholder script:**
   ```bash
   uv run python scripts/generate_coloring_placeholders.py
   ```
   This writes directly to `frontend/assets/svg/coloring/page-{5..9}-*.svg`, replacing the 170-byte stubs.

4. **Verify the new SVGs** pass the content-quality test:
   ```bash
   uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v
   ```
   Both `test_all_nine_coloring_svgs_exist` and `test_all_coloring_svgs_have_real_art` should pass.

5. **Spot-check SVG validity** — open one of the generated SVGs to verify it has proper XML structure, viewBox, and visible path data:
   ```bash
   head -5 frontend/assets/svg/coloring/page-5-forest.svg
   grep -c '<path' frontend/assets/svg/coloring/page-5-forest.svg
   ```

## Must-Haves

- [ ] `test_all_coloring_svgs_have_real_art` test added to `TestColoringSVGAssets` class
- [ ] `scripts/generate_coloring_placeholders.py` created and generates 5 scene-themed SVGs
- [ ] Each generated SVG is 1024x1024, valid XML, B&W outlines, ≥8 `<path` elements
- [ ] All 5 stub SVGs in `frontend/assets/svg/coloring/` replaced with real placeholder art
- [ ] Both asset tests in `TestColoringSVGAssets` pass

## Verification

- `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v` — 2 tests pass
- `for f in frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg; do size=$(wc -c < "$f"); count=$(grep -c '<path' "$f"); echo "$f: ${size}B, $count paths"; done` — each file >1000 bytes and ≥8 paths

## Inputs

- `tests/test_trace_coloring.py` — existing test file to extend with content-quality test
- `scripts/generate_dressup_outlines.py` — reference for the `_build_placeholder_svg()` pattern (1024x1024 B&W outline SVG with geometric shapes)
- `frontend/assets/svg/coloring/page-5-forest.svg` — current 170-byte stub to replace
- `frontend/assets/svg/coloring/page-6-treasure.svg` — current 170-byte stub to replace
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — current 170-byte stub to replace
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — current 170-byte stub to replace
- `frontend/assets/svg/coloring/page-9-starfish.svg` — current 170-byte stub to replace

## Expected Output

- `tests/test_trace_coloring.py` — extended with `test_all_coloring_svgs_have_real_art` in `TestColoringSVGAssets`
- `scripts/generate_coloring_placeholders.py` — new script that generates 5 placeholder coloring page SVGs
- `frontend/assets/svg/coloring/page-5-forest.svg` — real placeholder SVG (≥8 paths, >1KB)
- `frontend/assets/svg/coloring/page-6-treasure.svg` — real placeholder SVG (≥8 paths, >1KB)
- `frontend/assets/svg/coloring/page-7-jellyfish.svg` — real placeholder SVG (≥8 paths, >1KB)
- `frontend/assets/svg/coloring/page-8-whirlpool.svg` — real placeholder SVG (≥8 paths, >1KB)
- `frontend/assets/svg/coloring/page-9-starfish.svg` — real placeholder SVG (≥8 paths, >1KB)
