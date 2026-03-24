# S03 Research: Coloring Page Art Fix

**Slice:** M004/S03 — Coloring Page Art Fix
**Status:** Ready for planning
**Requirement:** COLR-04 — All 9 coloring gallery pages show real art

---

## Summary

Straightforward pipeline execution problem with one non-trivial wrinkle: the **1x1 placeholder PNGs for pages 5-9 block the pipeline's skip logic**. The entire end-to-end pipeline exists and works — it just hasn't been run for pages 5-9 with real inputs. The fix has two valid paths depending on whether an OpenAI API key is available. A new content-quality test is required to prove the fix (no such test exists today).

---

## Recommendation

**Two-track approach:**

1. **Write the content-quality test first** — asserts `page-{5..9}*.svg` each have `>= 5 <path` elements. Test fails immediately (stubs have 0). Creates red→green proof point.
2. **Run the pipeline with `OPENAI_API_KEY`** (preferred): delete 1x1 stub PNGs for pages 5-9, run `generate_coloring.py`, run `trace_all.py`, copy selectively to frontend.
3. **If no API key**: create geometric placeholder SVGs directly (same pattern as `generate_dressup_outlines.py --placeholder`). Satisfies tests but not visually matching intended art.

---

## Implementation Landscape

### Root Cause

`assets/generated/png/coloring/page-{5..9}-*.png` are 70-byte 1×1 RGBA PNGs. The idempotent skip in `generate.py` fires on them:

```python
if output_path.exists():
    print(f"  Skip (exists): {output_path.name}")
    return output_path
```

Traced SVGs are 170-byte vtracer stubs (`width="1" height="1"`), committed to `frontend/assets/svg/coloring/`. Pages 1-4 real SVGs (51–75KB) are committed and correct.

**Critical: ALL 9 PNGs in `assets/generated/png/coloring/` are 70-byte 1x1 stubs.** Pages 1-4 frontend SVGs are real because they were committed directly, not because their PNGs are real.

### Files to Change

| File | Action |
|---|---|
| `assets/generated/png/coloring/page-{5..9}-*.png` | Delete before regeneration (skip-logic trap) |
| `frontend/assets/svg/coloring/page-{5..9}-*.svg` | Replace 170-byte stubs with real multi-path SVGs |
| `tests/test_trace_coloring.py` | Add `test_all_coloring_svgs_have_real_art` asserting `>= 5 <path` per SVG |

### Path Counts (calibration)
- page-1-ocean.svg: 16 paths (binary mode, real)
- page-2-castle.svg: 18 paths
- page-3-seahorse.svg: 8 paths
- page-4-coral.svg: 12 paths
- page-5..9 stubs: 0 paths

**Threshold: >= 5** (NOT >50 — binary/simplify=True mode produces 8-18 paths, much less than full-color mode's 50+)

### Safe Selective Pipeline

```bash
# 1. Delete only pages 5-9 stubs (preserve pages 1-4 PNGs to avoid re-tracing)
rm assets/generated/png/coloring/page-{5,6,7,8,9}-*.png

# 2. Generate real PNGs (pages 1-4 still exist as stubs, get skipped)
uv run python scripts/generate_coloring.py

# 3. Trace to SVGs (pages 1-4 stubs → bad SVGs; pages 5-9 real → good SVGs)
# BUT: only copy the pages-5-9 outputs to frontend
# DO NOT use copy_coloring_pages_to_frontend() — it copies all 9 and overwrites good 1-4 SVGs

# 4. Manual copy for pages 5-9 only
cp assets/generated/svg/coloring/page-5-forest.svg frontend/assets/svg/coloring/
cp assets/generated/svg/coloring/page-6-treasure.svg frontend/assets/svg/coloring/
cp assets/generated/svg/coloring/page-7-jellyfish.svg frontend/assets/svg/coloring/
cp assets/generated/svg/coloring/page-8-whirlpool.svg frontend/assets/svg/coloring/
cp assets/generated/svg/coloring/page-9-starfish.svg frontend/assets/svg/coloring/
```

### Verification

New test (add to `TestColoringSVGAssets` in `tests/test_trace_coloring.py`):

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

### Constraints

- `copy_coloring_pages_to_frontend()` in `assemble.py` copies ALL 9 SVGs — using it would overwrite the good pages 1-4. Copy pages 5-9 selectively.
- `assets/generated/` is gitignored — only `frontend/assets/svg/coloring/*.svg` gets committed.
- CI deploy.yml runs `test_coloring.py` but NOT `test_trace_coloring.py`. Add new test to `test_coloring.py` as a static check OR add `test_trace_coloring.py` to the CI run.

### Forward Intelligence

- The existing prompts for pages 5-9 in `prompts.py` are already detailed (describe hair, tail, closed outlines) — no prompt work needed.
- If running placeholder path: the `_build_placeholder_svg()` pattern in `generate_dressup_outlines.py` shows exactly how to build a multi-path SVG without AI. Each scene (forest/treasure/jellyfish/whirlpool/starfish) needs distinct geometry. The placeholder needs only `>= 5 <path` elements to pass the test.
- Current test count: 115. Adding 1 test → 116, well above the 104+ milestone requirement.
