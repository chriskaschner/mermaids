# S02: Coloring Art Rework — Research

**Date:** 2026-03-23

## Summary

S02 delivers three active requirements: COLR-01 (coloring pages show hair/eyes/tail variety), COLR-02 (hair regions flood-fillable), COLR-03 (tail regions flood-fillable). Also in scope: DEBT-01 (remove debug overlay) and DEBT-02 (fix WebKit sparkle E2E failures).

The current coloring feature already works end-to-end: canvas flood fill, SVG overlay, undo, palette, memory release. The coloring pipeline also exists: `generate_coloring_pages()` produces 4 black-and-white outline PNGs via gpt-image-1, traced to SVG via `vtracer` (binary/`simplify=True` mode). What's missing is **variety and fillability**. All 4 current pages use the same generic base prompt — mermaids look similar and differ only by scene background. COLR-01 requires distinct hair, eye, and tail styles per page. COLR-02/03 require that hair and tail paths are closed shapes so flood fill stays within the region.

The fix is straightforward: extend `COLORING_PAGES` in `prompts.py` to 9 entries (one per character from the dress-up gallery), adding explicit hair/eyes/tail descriptions for each page. Then regenerate art, retrace, redeploy. The frontend gallery needs updating to show 9 pages instead of 4. Tests need to assert the new page count and variety. No architectural change is required — the entire pipeline already supports this.

There is also one pre-existing failing test: `test_color_swatch_recolors_paths` in `test_dressup.py` checks `path[fill]` attributes but the production code uses CSS `hue-rotate`. This test was supposed to be fixed in S01 per the task plan but wasn't updated in the final state. This must be fixed in S02 since it prevents the suite from reaching 102 passing.

DEBT-01 and DEBT-02 are surgical fixes in known files.

## Recommendation

**Expand COLORING_PAGES to 9 mermaid variants (mirroring DRESSUP_CHARACTERS) with explicit hair/eyes/tail style descriptions per page prompt. Fix the one failing test. Fix debug overlay and WebKit sparkle test.**

The 9-page approach directly parallels the 9-character dress-up gallery. Each coloring page is a full kawaii mermaid in a different scene, distinguished by a clearly different hairstyle (straight, afro puffs, braids, etc.), eye shape, and tail style per the `COLORING_BASE_PROMPT`. The existing pipeline handles everything else — generation is idempotent (skips existing PNGs), tracing uses `simplify=True` for binary outline mode, `copy_coloring_pages_to_frontend()` deploys to `frontend/assets/svg/coloring/`.

Flood-fillability of hair/tail depends entirely on the AI art quality. vtracer in binary mode traces black outlines as closed paths. The existing 4 pages already work for flood fill. Adding explicit style variety to the prompt increases the probability that hair and tail are drawn as discrete closed regions rather than merged background shapes.

## Implementation Landscape

### Key Files

- `src/mermaids/pipeline/prompts.py` — `COLORING_PAGES` list (currently 4 entries). Needs expansion to 9 entries, each with a distinct `prompt_detail` that includes explicit hair style, eye style, and tail style description.
- `src/mermaids/pipeline/generate.py` — `generate_coloring_pages()` iterates `COLORING_PAGES`. Works as-is; no changes needed.
- `scripts/generate_coloring.py` — CLI entry point for generation. Works as-is.
- `scripts/trace_all.py` — `trace_coloring_pages()` traces all PNGs in `GENERATED_PNG_DIR/coloring/`. Works as-is.
- `src/mermaids/pipeline/assemble.py` — `copy_coloring_pages_to_frontend()` copies traced SVGs to `frontend/assets/svg/coloring/`. Works as-is.
- `frontend/js/coloring.js` — `COLORING_PAGES` array (4 entries, ids page-1-ocean through page-4-coral). Needs 9 entries to match new pages.
- `frontend/js/app.js` — `renderColoring()` builds gallery from `COLORING_PAGES`. Works as-is (dynamic). Also contains `_initDebug()` debug overlay — DEBT-01 removes this and the triple-tap wiring.
- `tests/test_coloring.py` — `test_gallery_shows_thumbnails` asserts `count >= 4`. This will pass with 9 pages, but the test should be updated to assert `>= 9` to pin variety. No structural changes needed.
- `tests/test_generate.py` — `TestGenerateColoringPages::test_generate_coloring_pages_produces_all_four` asserts `len(results) == 4`. **Must be updated to 9**.
- `tests/test_dressup.py::TestColorSwatches::test_color_swatch_recolors_paths` — **Failing test**. Currently asserts `path[fill] == '#ff69b4'` but production uses CSS `hue-rotate`. Fix: assert `svg.style.filter.includes('hue-rotate')` (matching the pattern documented in KNOWLEDGE.md).
- `frontend/js/sparkle.js` — May contain WebKit-specific bug causing DEBT-02 test failures. Read before fixing.
- `tests/test_e2e.py` — Contains WebKit sparkle tests that fail.

### Page IDs for 9 Coloring Pages

Recommended IDs following the existing naming pattern:
```
page-1-ocean        (existing, keep)
page-2-castle       (existing, keep)
page-3-seahorse     (existing, keep)
page-4-coral        (existing, keep)
page-5-forest       (new)
page-6-treasure     (new)
page-7-jellyfish    (new)
page-8-whirlpool    (new)
page-9-starfish     (new)
```

Each page prompt must specify a distinct hair style and tail style. Example mapping to `DRESSUP_CHARACTERS` features (for cross-activity consistency):

| Page | Hair Style | Eye Style | Tail Style | Scene |
|------|------------|-----------|------------|-------|
| page-1-ocean | long wavy hair | round big eyes | rounded fin tail | ocean with fish |
| page-2-castle | twin pigtails with bows | big eyes | ribbon-like tail | underwater castle |
| page-3-seahorse | long curly hair | warm eyes | scalloped tail | seahorse scene |
| page-4-coral | straight long braid | big dark eyes | fan-shaped tail | coral reef |
| page-5-forest | curly afro puffs | sparkle eyes | star-shaped tail | kelp forest |
| page-6-treasure | long braids with beads | wide eyes | rounded fin tail | treasure chest |
| page-7-jellyfish | coily hair with flower | bright eyes | flowing tail | jellyfish meadow |
| page-8-whirlpool | silver locs with tips | big bright eyes | deep fin tail | whirlpool vortex |
| page-9-starfish | short bob with bangs | starry eyes | iridescent tail | starfish beach |

### Build Order

1. **Fix `test_color_swatch_recolors_paths`** — Highest priority, currently failing. Change the test assertion to check `svg.style.filter` for `hue-rotate` instead of `path[fill]`. No production code changes needed.
2. **Expand `COLORING_PAGES` in `prompts.py`** — Add 5 new page entries (pages 5-9) with distinct hair/tail/eye descriptions. Update `frontend/js/coloring.js` `COLORING_PAGES` array to match.
3. **Update `test_generate.py`** — Change `len(results) == 4` to `len(results) == 9`.
4. **Art generation** — Run `uv run python scripts/generate_coloring.py` (existing 4 skip, 5 new generated). Then `uv run python scripts/trace_all.py`. Then `copy_coloring_pages_to_frontend()`.
5. **Fix DEBT-01** — Remove `_initDebug()` function and its wiring in `app.js` (triple-tap handler, `?debug=1` URL check).
6. **Fix DEBT-02** — Investigate and fix WebKit sparkle E2E failures.
7. **Tests** — Run full suite, verify 102+ pass.

### Verification Approach

```bash
# After code changes (before art generation):
uv run pytest tests/test_generate.py tests/test_dressup.py -v

# After art generation and deploy:
uv run pytest -q  # Full suite, should reach 102+ passing

# Gallery variety check:
uv run pytest tests/test_coloring.py::TestColoringGallery -v
```

Observable behavior:
- Coloring gallery shows 9 thumbnails (was 4)
- Each page shows a distinct hair/tail style (visually verifiable in browser)
- Flood fill on a hair region colors hair area without leaking to background
- Flood fill on a tail region colors tail area without leaking

## Constraints

- **No bundler/npm** — All frontend is vanilla ES modules. Any JS changes must be plain module syntax.
- **iPad Safari target** — `CANVAS_SIZE = 1024`, `willReadFrequently: true`, canvas released on navigation. These are already implemented in `coloring.js` and must not regress.
- **vtracer binary mode** — Coloring pages must use `simplify=True` in `trace_to_svg()` (binary/outline mode). This is already enforced in `trace_coloring_pages()`. Do NOT switch to full-color mode — that produces too many paths and is for dress-up only.
- **Idempotent pipeline** — Generation and tracing skip existing files. The 4 existing SVGs stay as-is unless manually deleted.
- **`FILL_TOLERANCE = 48`** — Already tuned in `coloring.js` for anti-aliased edges. Do not change.
- **Flood-fill fillability depends on art quality** — The prompt can encourage it but cannot guarantee closed regions. If a generated page fails COLR-02/03 on visual inspection, regenerate that specific page with a more explicit prompt ("mermaid hair is a single closed shape filled with white, outlined in black").

## Common Pitfalls

- **Same-page IDs** — `COLORING_PAGES` in `prompts.py` and `frontend/js/coloring.js` must stay in sync. Both use the `id` field for filename matching. If they drift, the frontend fetches the wrong SVG.
- **Path fillability vs. vtracer artifact** — vtracer in binary mode produces closed paths for distinct colored regions in a B&W image. If the AI generates hair that blends into the background (no clear outline), vtracer will not produce a closed region. The prompt must explicitly request "single enclosed black outline of the mermaid's hair."
- **Test count assertions** — `test_generate_coloring_pages_produces_all_four` has `== 4`. Update this or the test will fail against the new 9-page list.
- **Recolor test** — `test_color_swatch_recolors_paths` fails because it checks `fill` attribute. The fix is test-side only (assert `hue-rotate` filter). Production code is correct.
- **Debug overlay DEBT-01** — The `_initDebug()` function is ~60 lines in `app.js`. Remove the function body AND its two call sites (the `?debug=1` check in DOMContentLoaded and the triple-tap event listener on the home nav icon).

## Open Risks

- **AI art closed-region quality** — gpt-image-1 B&W coloring pages occasionally produce hair that merges with backgrounds or produces non-closed path segments. If COLR-02/03 can't be demonstrated on generated art, the test strategy must rely on structural assertions (path count, presence of dark outline paths) rather than actual flood-fill correctness of specific regions.
- **DEBT-02 WebKit specifics** — The WebKit sparkle test failures are pre-existing. Need to read `test_e2e.py` and `sparkle.js` to understand root cause before estimating fix complexity.
