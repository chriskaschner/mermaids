---
id: T03
parent: S01
milestone: M004
provides:
  - '"Color This!" button in dress-up view wired to dressupState.activeCharacter'
  - Router parses ?character= query param from hash (#/coloring?character=mermaid-N)
  - renderColoringForCharacter() loads dressup-coloring outlines on coloring canvas
  - Back button in character coloring view returns to #/dressup
  - 4 new E2E tests in TestDressUpToColoring class
  - All 9 dressup-coloring SVGs fixed for strict XML validity (no double-hyphens in comments)
key_files:
  - frontend/js/app.js
  - frontend/css/style.css
  - tests/test_e2e.py
  - frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg
  - scripts/generate_dressup_outlines.py
key_decisions:
  - renderColoringForCharacter() is a standalone async function duplicating the openColoringPage pattern — keeps gallery flow and dressup flow cleanly separated
  - Router query-param parsing done inline in router() with split("?") + split("&") — avoids URLSearchParams for compatibility with the existing hash-based routing
  - All 9 dressup-coloring SVGs fixed in-place; generation script patched to prevent recurrence of invalid XML comments
patterns_established:
  - Chromium strict XML validation — SVG comments must not contain -- (double hyphen) or non-ASCII; both cause img.onerror to fire silently; bisect by comparing full-file vs. stripped-comment blob URL loads
  - Hash-with-query-params router pattern: rawHash.split("?") gives [route, queryString]; then split("&").forEach(pair => split("=")) populates params dict
observability_surfaces:
  - console.error logged when renderColoringForCharacter SVG load fails (includes svgUrl)
  - .error div rendered in #app if outline SVG fails to load
  - "#coloring-canvas" id on canvas for DevTools / test selectors
  - Network tab shows dressup-coloring/mermaid-N-outline.svg fetch
  - URL hash contains character= param — inspect window.location.hash to verify routing
duration: ~75m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T03: Add "Color This!" button and dress-up → coloring routing

**Wired the full dress-up → coloring pipeline: "Color This!" button navigates to coloring canvas with active character's B&W outline loaded; router parses ?character= query params; back button returns to dress-up; all 111 tests pass.**

## What Happened

**Import:** Added `state as dressupState` to the `dressup.js` import in `app.js`.

**"Color This!" button:** Inserted `<button class="color-this-btn" ...>🎨 Color This!</button>` at bottom of `.selection-panel` in `renderDressUp()`. Click handler reads `dressupState.activeCharacter` and sets `window.location.hash = "#/coloring?character=" + characterId`.

**Router update:** `router()` now splits `rawHash` on `?` to extract query string, then builds a `params` dict. When `hash === "coloring"` and `params.character` is set, calls `renderColoringForCharacter(params.character)` and returns early.

**`renderColoringForCharacter(characterId)`:** New async function structurally identical to `openColoringPage()` but loads SVG from `assets/svg/dressup-coloring/${characterId}-outline.svg`. Back button sets `window.location.hash = "#/dressup"`. Full error handling with `console.error` and `.error` div.

**CSS:** `.color-this-btn` is full-width, min-height 60px, coral-to-orange gradient, bold, 18px border-radius, scale-on-press — child-friendly and visually prominent.

**SVG XML validity fix (unplanned):** All 9 `dressup-coloring` outline SVGs were rejected by Chromium's strict XML parser via silent `img.onerror`. Root cause: invalid XML in comments — (1) double-hyphen `--` sequences from `<!-- --placeholder -->` and `<!-- ── Head ── -->`, (2) Unicode box-drawing `─` characters. Fixed all 9 files and patched `scripts/generate_dressup_outlines.py` to avoid recurrence.

**E2E tests:** Added `TestDressUpToColoring` with 4 tests covering button visibility, navigation with default character, navigation with mermaid-3 selected, and back-button behaviour.

## Verification

- `pytest tests/test_e2e.py -x -q` → 14 passed (10 original + 4 new)
- `pytest tests/ -x -q` → 111 passed (full suite, no regressions)
- All 4 slice grep checks pass

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `.venv/bin/python -m pytest tests/test_e2e.py -x -q` | 0 | ✅ pass | 14.1s |
| 2 | `.venv/bin/python -m pytest tests/ -x -q` | 0 | ✅ pass | 44.8s |
| 3 | `grep -q 'Color This' frontend/js/app.js` | 0 | ✅ pass | <1s |
| 4 | `grep -q 'renderColoringForCharacter' frontend/js/app.js` | 0 | ✅ pass | <1s |
| 5 | `test -f frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` | 0 | ✅ pass | <1s |
| 6 | `test -f frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` | 0 | ✅ pass | <1s |
| 7 | `grep -q 'hair-group' frontend/assets/svg/dressup/mermaid-1.svg` | 0 | ✅ pass | <1s |
| 8 | `grep -q '#hair-group' frontend/js/dressup.js` | 0 | ✅ pass | <1s |

## Diagnostics

- **Canvas not appearing:** Check console for `renderColoringForCharacter: failed to load` — then Network tab for outline SVG status. 200 + error = SVG XML validity issue (check for `--` in comments).
- **Wrong character:** `dressupState.activeCharacter` in DevTools console.
- **Back goes to gallery:** Verify `.back-btn` handler in `renderColoringForCharacter` sets `window.location.hash = "#/dressup"`.
- **Hair not isolated:** `document.querySelector('#hair-group').style.filter` should contain `hue-rotate`; root `svg.style.filter` should be empty.

## Deviations

**SVG XML validity fix (unplanned):** The T02 placeholder SVGs contained invalid XML in comments causing silent Chromium rejection. Diagnosed via bisection (blob URL with/without comments). Fixed all 9 files and the generation script. Added pattern to KNOWLEDGE.md.

## Known Issues

Placeholder art is geometric, not character-faithful. Run `python scripts/generate_dressup_outlines.py` with `OPENAI_API_KEY` set to replace with AI-generated outlines.

## Files Created/Modified

- `frontend/js/app.js` — added dressupState import, "Color This!" button, router query-param parsing, renderColoringForCharacter()
- `frontend/css/style.css` — added .color-this-btn styles
- `tests/test_e2e.py` — added TestDressUpToColoring with 4 E2E tests
- `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` — fixed invalid XML in comments (9 files)
- `scripts/generate_dressup_outlines.py` — fixed comment templates to ASCII-only, no double-hyphens
- `.gsd/KNOWLEDGE.md` — added SVG XML comment validity gotcha
