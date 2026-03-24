---
estimated_steps: 5
estimated_files: 5
skills_used: []
---

# T01: Expand coloring pages to 9 with distinct hair/eyes/tail variety

**Slice:** S02 — Coloring Art Rework
**Milestone:** M003

## Description

Expand the coloring page definitions from 4 generic pages to 9 pages with distinct hair style, eye style, and tail style descriptions per page. This mirrors the 9-character diversity from the dress-up gallery. Each page prompt must explicitly request closed black outlines for hair and tail regions so vtracer produces closed SVG paths suitable for flood fill.

Both the Python pipeline (`prompts.py`) and the frontend JS (`coloring.js`) must have matching 9-entry arrays. The test that asserts page count (`test_generate.py`) must be updated from `== 4` to `== 9`. The gallery thumbnail test (`test_coloring.py`) must assert `>= 9`.

**Important context:** The coloring pipeline already works end-to-end — `generate_coloring_pages()` iterates `COLORING_PAGES` and the frontend `renderColoring()` dynamically renders from its JS array. No architectural changes needed; this is purely data expansion + test updates.

## Steps

1. **Expand `COLORING_PAGES` in `src/mermaids/pipeline/prompts.py`** — Add 5 new entries (page-5-forest through page-9-starfish). Each entry needs `id` and `prompt_detail`. The `prompt_detail` must include: (a) distinct hair style, (b) distinct eye style, (c) distinct tail style, (d) scene description, and (e) explicit language: "The mermaid's hair is a single enclosed shape with a clear black outline. The mermaid's tail is a single enclosed shape with a clear black outline." Use this mapping:

   | ID | Hair | Eyes | Tail | Scene |
   |---|---|---|---|---|
   | page-5-forest | curly afro puffs | sparkle eyes | star-shaped tail | kelp forest |
   | page-6-treasure | long braids with beads | wide eyes | rounded fin tail | treasure chest |
   | page-7-jellyfish | coily hair with flower | bright eyes | flowing tail | jellyfish meadow |
   | page-8-whirlpool | silver locs with tips | big bright eyes | deep fin tail | whirlpool vortex |
   | page-9-starfish | short bob with bangs | starry eyes | iridescent tail | starfish beach |

2. **Expand `COLORING_PAGES` in `frontend/js/coloring.js`** — Add 5 matching entries after the existing 4. Format: `{ id: "page-5-forest", label: "Kelp Forest", file: "assets/svg/coloring/page-5-forest.svg" }`. Labels should be child-friendly scene names.

3. **Update `tests/test_generate.py`** — In `TestGenerateColoringPages::test_generate_coloring_pages_produces_all_four`: rename to `test_generate_coloring_pages_produces_all_nine`, change `assert len(results) == 4` to `assert len(results) == 9`. Add a new test `test_coloring_page_prompts_have_distinct_styles` that imports `COLORING_PAGES` from `prompts.py` and asserts: (a) `len(COLORING_PAGES) == 9`, (b) all IDs are unique, (c) each `prompt_detail` is unique.

4. **Update `tests/test_coloring.py`** — In `TestColoringGallery::test_gallery_shows_thumbnails`: change `assert thumbs.count() >= 4` to `assert thumbs.count() >= 9`.

5. **Update `src/mermaids/pipeline/generate.py`** — Change the docstring of `generate_coloring_pages()` from "Generate all 4 coloring page PNGs" to "Generate all coloring page PNGs" (remove hardcoded count).

## Must-Haves

- [ ] `COLORING_PAGES` in `prompts.py` has exactly 9 entries, each with a unique `id` and distinct `prompt_detail` mentioning specific hair style, eye style, tail style
- [ ] Each new prompt_detail includes explicit "single enclosed shape with clear black outline" language for hair and tail
- [ ] `COLORING_PAGES` in `coloring.js` has exactly 9 entries with matching IDs
- [ ] `test_generate_coloring_pages_produces_all_nine` asserts `len(results) == 9`
- [ ] `test_gallery_shows_thumbnails` asserts `thumbs.count() >= 9`
- [ ] New test asserts all 9 page prompts have distinct content
- [ ] Full test suite passes: `uv run pytest -q` shows 102+ passed

## Verification

- `uv run pytest tests/test_generate.py::TestGenerateColoringPages -v` — both tests pass (count=9, distinct styles)
- `uv run pytest tests/test_coloring.py::TestColoringGallery -v` — passes with `>= 9` assertion
- `uv run pytest -q` — 102+ passed (existing 4 coloring SVGs still work for E2E tests; new 5 pages won't have SVGs yet so E2E tests that open pages use the first page which exists)
- `grep -c '"page-' src/mermaids/pipeline/prompts.py` returns 9
- `grep -c '"page-' frontend/js/coloring.js` returns 9

## Inputs

- `src/mermaids/pipeline/prompts.py` — existing 4-entry COLORING_PAGES to expand
- `frontend/js/coloring.js` — existing 4-entry COLORING_PAGES JS array to expand
- `tests/test_generate.py` — existing test asserting `len(results) == 4` to update
- `tests/test_coloring.py` — existing gallery test asserting `>= 4` to update
- `src/mermaids/pipeline/generate.py` — docstring referencing "4" to update

## Expected Output

- `src/mermaids/pipeline/prompts.py` — 9-entry COLORING_PAGES with distinct hair/eyes/tail per page
- `frontend/js/coloring.js` — 9-entry COLORING_PAGES JS array with matching IDs and labels
- `tests/test_generate.py` — updated count assertion + new distinctness test
- `tests/test_coloring.py` — updated gallery assertion to >= 9
- `src/mermaids/pipeline/generate.py` — updated docstring
