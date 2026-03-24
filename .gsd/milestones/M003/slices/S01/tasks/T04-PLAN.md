# T04: Fix hair paths that bleed beyond hair region

**Slice:** S01
**Milestone:** M003

## Goal
Clip or redraw hair paths in all 9 mermaid character SVGs so they are bounded to the visible hair zone, preventing CSS hue-rotate from visually recoloring body/skin/tail areas through oversized underlying hair paths.

## Must-Haves

### Truths
Observable behaviors that must be true when this task is done:
- "Applying hue-rotate to any character visually changes only the hair color, not the skin or tail"
- "All 9 mermaid SVGs render identically to before when no hue-rotate is applied (visual fidelity preserved)"
- "All 102 existing tests still pass"

### Artifacts
Files that must exist with real implementation (not stubs):
- `frontend/assets/svg/dressup/mermaid-{1..9}.svg` — 9 updated SVGs with hair paths bounded to hair-visible region
- `frontend/assets/svg/mermaid.svg` — updated default mermaid (copy of mermaid-1)

### Key Links
Critical wiring between artifacts:
- Hair path bounding boxes must not extend below ~y 300 (aligned with REGIONS["hair"] = y 0–290 in edit.py)
- `assemble_combo_svg()` in assemble.py should remain compatible (no structural SVG changes, just path geometry)

## Steps
1. Analyze each mermaid-{1..9}.svg to identify which paths are hair (typically path[0] and path[1] — dark hair outline and hair fill, identifiable by large y-span and hair-colored fills)
2. For each hair path, apply a clipPath or manually trim the path data to bound it within y ≈ 0–300 (the visible hair zone above the face/body)
3. Verify that the trimmed SVGs render visually identical to the originals at rest (no hue-rotate applied)
4. Verify that hue-rotate applied to a trimmed SVG only visually shifts the hair, not skin/body/tail
5. Copy updated mermaid-1.svg as mermaid.svg (default character)
6. Run full test suite to confirm no regressions

## Context
- The hair issue was identified during the S01 UAT / discuss phase. vtracer produces paths that fill the entire shape area, and hair wraps behind the body in the AI art, producing paths spanning y 59–970 on a 1024×1024 canvas.
- The existing REGIONS dict in edit.py defines hair as y 0–290. This is the target bounding zone.
- The simplest approach is SVG `<clipPath>` elements that mask hair paths to the hair region, preserving the original path data.
- Alternative: programmatically split paths at the clip boundary. More complex but produces smaller SVGs.
- Decision D001 locks this approach.

## Expected Output
- `frontend/assets/svg/dressup/mermaid-1.svg` — updated with `<defs><clipPath id="hair-clip">` and `clip-path="url(#hair-clip)"` on paths 0 and 1
- `frontend/assets/svg/dressup/mermaid-2.svg` — updated (paths 1 and 3, skipping BG rect at path 0)
- `frontend/assets/svg/dressup/mermaid-3.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/dressup/mermaid-4.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/dressup/mermaid-5.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/dressup/mermaid-6.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/dressup/mermaid-7.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/dressup/mermaid-8.svg` — updated (paths 1 and 3, skipping BG rect at path 0)
- `frontend/assets/svg/dressup/mermaid-9.svg` — updated (paths 0 and 1)
- `frontend/assets/svg/mermaid.svg` — copy of updated mermaid-1.svg

## Observability Impact
- **Clip presence check:** `grep -c 'hair-clip' frontend/assets/svg/dressup/mermaid-{1..9}.svg` — should return 3 for each (1 in defs + 2 on paths)
- **Failure state:** If a character SVG is missing the clipPath, the hair paths bleed below y=310 and hue-rotate visually affects body/tail areas with hair-colored pixels. No JS error — only visual artifact.
- **Visual verification:** Load `http://localhost:8080#/dressup`, click a color swatch, observe that only the hair zone (top of character, approx y=0–310) is affected by the hue shift in the hair paths specifically. Skin/tail paths are also hue-shifted by design (hue-rotate applies to whole SVG), but hair-colored pixels no longer bleed into body/tail.
- **Regression signal:** `uv run pytest -q` — 102 tests; any failure indicates a regression in SVG structure or frontend JS expectations.
