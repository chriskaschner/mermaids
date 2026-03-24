# S03: Coloring Page Art Fix — UAT Script

**Preconditions:**
- App served from `frontend/` directory (e.g. `python -m http.server 8082 --directory frontend`)
- Browser open, viewport ≥1024×768
- No prior navigation state (fresh load or hard refresh)

---

## Test Case 1: All 9 Gallery Thumbnails Are Visible

1. Navigate to `http://localhost:8082/#/coloring`
2. Wait for gallery to render (9 thumbnail buttons should appear)
3. **Expected:** All 9 thumbnails show visible black-outline mermaid line art on white background. None are blank white rectangles.
4. **Expected:** Thumbnails are labeled: Ocean Mermaid, Mermaid Castle, Seahorse Friend, Coral Reef, Kelp Forest, Treasure Chest, Jellyfish Meadow, Whirlpool Vortex, Starfish Beach.

**Pass criteria:** 9 out of 9 thumbnails render non-blank artwork.

---

## Test Case 2: Page 5 (Kelp Forest) Loads on Canvas

1. From the coloring gallery (`#/coloring`), click the "Kelp Forest" thumbnail
2. Wait for coloring canvas to load
3. **Expected:** Canvas displays a mermaid figure with kelp stalks, bubbles, and sandy ocean floor. Color picker palette is visible below the canvas.
4. **Expected:** The mermaid outline has clear black lines suitable for flood-fill coloring.

**Pass criteria:** Canvas is non-blank and shows recognizable scene elements.

---

## Test Case 3: Page 6 (Treasure Chest) Loads on Canvas

1. Navigate back to gallery (`#/coloring`)
2. Click the "Treasure Chest" thumbnail
3. **Expected:** Canvas displays a mermaid with a treasure chest, coins, gems, and ocean floor.

**Pass criteria:** Canvas is non-blank with distinct scene elements different from page 5.

---

## Test Case 4: Pages 7-9 Each Load Distinct Scenes

1. For each of: Jellyfish Meadow, Whirlpool Vortex, Starfish Beach
   a. Navigate to `#/coloring`
   b. Click the respective thumbnail
   c. **Expected:** Canvas loads with a mermaid + unique scene elements (jellyfish bells, vortex rings, starfish/shells respectively)

**Pass criteria:** Each page loads with visually distinct content. No two scenes are identical.

---

## Test Case 5: Pages 1-4 Still Work

1. Navigate to `#/coloring`
2. Click "Ocean Mermaid" (page 1)
3. **Expected:** Canvas loads with the original AI-traced mermaid art (higher detail than pages 5-9)
4. Repeat for pages 2-4 (Mermaid Castle, Seahorse Friend, Coral Reef)

**Pass criteria:** All 4 original pages still load correctly — no regression from the page 5-9 work.

---

## Test Case 6: Content-Quality Test Gate

1. Run: `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v`
2. **Expected:** Both tests pass:
   - `test_all_nine_coloring_svgs_exist` — all 9 SVG files present
   - `test_all_coloring_svgs_have_real_art` — all 9 SVGs have ≥5 `<path` elements

**Pass criteria:** 2/2 tests pass, exit code 0.

---

## Test Case 7: SVG Path Count Audit

1. Run: `for f in frontend/assets/svg/coloring/page-{5,6,7,8,9}-*.svg; do count=$(grep -c '<path' "$f"); echo "$f: $count paths"; test "$count" -ge 5 || echo "FAIL: $f"; done`
2. **Expected:** Each file reports ≥5 paths. No "FAIL" output.

**Pass criteria:** Zero FAIL lines.

---

## Edge Case: Stub Regression Detection

1. Replace `page-5-forest.svg` with a stub: `echo '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>' > frontend/assets/svg/coloring/page-5-forest.svg`
2. Run: `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets::test_all_coloring_svgs_have_real_art -v`
3. **Expected:** Test FAILS with assertion message naming `page-5-forest.svg: 0 paths`
4. Restore the real SVG: `git checkout frontend/assets/svg/coloring/page-5-forest.svg`

**Pass criteria:** The content-quality test catches stubs and names the failing file.

---

## Edge Case: Generator Script Idempotency

1. Run: `uv run python scripts/generate_coloring_placeholders.py`
2. **Expected:** Script reports all 5 files as already having real art (>500 bytes) and skips them.
3. Run content-quality test again: `uv run pytest tests/test_trace_coloring.py::TestColoringSVGAssets -v`
4. **Expected:** Still passes — script did not corrupt existing files.

**Pass criteria:** Script is safe to re-run without data loss.
