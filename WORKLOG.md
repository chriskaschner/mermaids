# Phase 8 Work Log - Dress-Up Art Rework

## Direction Change: Part-Based -> Character Gallery

The original plan (multi-layer part swapping) failed because gpt-image-1 edit API
outputs full characters, not isolated parts. Clipping/compositing approaches all
produced visible seams. Decision: switch to **character gallery with 9 diverse mermaids**.

## What's Done

### Pipeline code updated:
- `prompts.py`: DRESSUP_CHARACTERS list with 9 diverse skin tones/features (replaces DRESSUP_VARIANTS)
- `generate.py`: `generate_dressup_characters()` function added (uses generate API, not edit API)
- `assemble.py`: `assemble_combo_svg()` and `deploy_characters_to_frontend()` added
- `edit.py`: Old `composite_all_combinations()` kept but no longer used; fixed broken DRESSUP_VARIANTS import

### Frontend code updated:
- `dressup.js`: Rewritten for flat character gallery (selectCharacter, CHARACTERS array, COLORS + SKIN_TONES)
- `app.js`: renderDressUp() rewritten with character gallery buttons + combined color/skin-tone swatches + undo
- `app.js`: Fixed COLORS name collision (DRESSUP_COLORS vs COLORING_COLORS)
- `app.js` + `dressup.js`: Removed cache buster `?t=` from fetch calls

### CSS updated:
- `.character-gallery`: 3x3 grid, max-width 280px, auto-centered
- `.char-btn`: aspect-ratio 1, 60pt+ touch targets, selected state with purple border
- `.color-row` + `.color-section`: horizontal scrollable swatch strip with undo button

### Art generated and deployed:
- 9 character PNGs generated via gpt-image-1 (mermaid-1 through mermaid-9)
- Traced to full-color SVG via vtracer (simplify=False)
- Assembled (background stripped, id="mermaid-svg" added)
- Deployed to `frontend/assets/svg/dressup/mermaid-{1..9}.svg`
- mermaid-1 copied as default `frontend/assets/svg/mermaid.svg`

### Cleanup:
- Removed 81 old combo SVGs from frontend
- Removed 13 old part SVGs (acc-*, body.svg, eye-*, hair-*, tail-*) from frontend

### Tests updated:
- `test_dressup.py`: Full rewrite for character gallery (14 tests)
- `test_assemble.py`: Rewritten for assemble_combo_svg + deploy_characters_to_frontend (9 tests)
- `test_masks.py`: Updated prompts tests for DRESSUP_CHARACTERS, added generate_dressup_characters test (11 tests)
- `test_generate.py`: Added TestGenerateDressupCharacters (1 test)
- `test_e2e.py`: Updated for character gallery (no data-region, celebration sparkles)
- All 102 tests passing

### Scripts updated:
- `scripts/generate_dressup.py`: Uses generate_dressup_characters() instead of old variants
- `scripts/trace_all.py`: trace_dressup_characters() reads mermaid-*.png (not parts/)
- `scripts/run_pipeline.py`: Full rewrite with `dressup` subcommand for character-only pipeline

### Review page:
- `frontend/review.html`: 3x3 grid preview of all 9 characters with descriptions

## Key Files Modified (uncommitted)
- src/mermaids/pipeline/prompts.py
- src/mermaids/pipeline/generate.py
- src/mermaids/pipeline/assemble.py
- src/mermaids/pipeline/edit.py
- frontend/js/dressup.js
- frontend/js/app.js
- frontend/css/style.css
- scripts/generate_dressup.py
- scripts/trace_all.py
- scripts/run_pipeline.py
- tests/test_dressup.py
- tests/test_assemble.py
- tests/test_masks.py
- tests/test_generate.py
- tests/test_e2e.py
- frontend/review.html (new)
- frontend/assets/svg/dressup/mermaid-{1..9}.svg (new)
- frontend/assets/svg/mermaid.svg (updated)
- assets/generated/png/dressup/mermaid-{1..9}.png (new)
- assets/generated/svg/dressup/mermaid-{1..9}.svg (new)
- assets/generated/svg/dressup/assembled/mermaid-{1..9}.svg (new)

## Design Decisions
- 9 characters for 3x3 grid on iPad
- Skin tones in color palette: #FDDCB5, #F5C5A3, #E8A97E, #D4915A, #C07840, #8D5524
- Character gallery is flat (no tabs/categories)
- Recoloring still works on active character's non-outline, non-skin, non-white paths
- Each character SVG is standalone (no layers, no defs+use structure)
