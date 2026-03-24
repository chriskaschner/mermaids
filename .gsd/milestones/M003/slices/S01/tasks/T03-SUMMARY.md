---
id: T03
parent: S01
milestone: M003
provides:
  - 102/102 tests passing including 14/14 dressup E2E tests
  - CSS hue-rotate recoloring verified on all 9 characters including dark-skinned mermaid-4
  - test_dressup.py updated to match hue-rotate implementation (was checking fill attributes)
  - Observability sections added to S01-PLAN.md and T03-PLAN.md
key_files:
  - tests/test_dressup.py
  - frontend/assets/svg/mermaid.svg
  - frontend/assets/svg/dressup/mermaid-1.svg
key_decisions:
  - CSS hue-rotate filter approach for recoloring confirmed correct over fill-attribute manipulation
patterns_established:
  - Test CSS filter state via `element.style.filter` not `path[fill]` attribute reads
observability_surfaces:
  - "`document.getElementById('mermaid-svg')?.style?.filter` — shows active hue-rotate value"
  - "`document.querySelector('.char-btn.selected')?.dataset?.character` — active character ID"
  - "Network 404 on `assets/svg/dressup/mermaid-*.svg` = character SVG missing"
  - "`#app .error` div = mermaid.svg fetch failure"
  - "`uv run pytest tests/test_dressup.py -v` — 14-test E2E coverage"
duration: 20min
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T03: 08-dress-up-art-rework 03

**Fixed the one failing dressup test by updating it to check CSS hue-rotate filter instead of fill attributes; all 102 tests now pass and recoloring is visually verified on all 9 characters including dark-skinned mermaid-4.**

## What Happened

T03's stated plan (delete old assets, run AI pipeline, assemble multi-layer SVG) was superseded by prior work: the codebase had already pivoted from multi-layer part-swapping to a flat 9-character gallery approach (documented in WORKLOG.md and `.planning/phases/08-dress-up-art-rework/.continue-here.md`). The art was already generated and deployed (commit `39336c0`). The actual remaining work was:

1. **One failing test** — `TestColorSwatches::test_color_swatch_recolors_paths` expected `fill="#ff69b4"` on SVG path elements after clicking a color swatch. The current implementation uses CSS `hue-rotate` on the `<svg>` element (not fill manipulation), so the test correctly failed. Updated test to assert `svg.style.filter.includes('hue-rotate')`.

2. **Stale undo test** — `test_undo_reverts_color` read `path[fill]` attributes, which hue-rotate never changes. Updated test to check that undo restores the CSS filter to its pre-recolor value.

3. **Visual verification** — Ran local server and confirmed in browser: gallery shows all 9 characters, character swapping works, hue-rotate recoloring works on all characters including mermaid-4 (dark-skinned, which had been the critical failing case for the old fill heuristic).

4. **Observability gaps** — Added `## Observability / Diagnostics` to S01-PLAN.md and `## Steps` + `## Observability Impact` to T03-PLAN.md as required by pre-flight.

## Verification

- `uv run pytest tests/test_dressup.py -v` → 14/14 passed
- `uv run pytest tests/test_assemble.py tests/test_masks.py -v` → 21/21 passed  
- `uv run pytest -q` → 102/102 passed
- Browser: loaded `http://localhost:8080#/dressup`, confirmed 9-button gallery, mermaid SVG visible with 23 paths (AI art), hue-rotate filter applies on swatch click (`hue-rotate(330deg)` for hot pink, `hue-rotate(180deg)` for teal), mermaid-4 (dark-skinned) fully recolors to teal confirming hue-rotate works on all skin tones

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run pytest tests/test_dressup.py -v` | 0 | ✅ pass | 8.24s |
| 2 | `uv run pytest tests/test_assemble.py tests/test_masks.py -v` | 0 | ✅ pass | 4.67s |
| 3 | `uv run pytest -q` | 0 | ✅ pass | 46.67s |
| 4 | Browser: `#mermaid-svg` visible + 23 paths | — | ✅ pass | visual |
| 5 | Browser: `.char-btn` count = 9 | — | ✅ pass | visual |
| 6 | Browser: hue-rotate filter on swatch click | — | ✅ pass | visual |
| 7 | Browser: mermaid-4 (dark skin) fully recolors | — | ✅ pass | visual |

## Diagnostics

- **Recolor state:** `document.getElementById('mermaid-svg')?.style?.filter` — returns `"hue-rotate(Xdeg)"` when recolor active, `""` after undo or on reset.
- **Active character:** `document.querySelector('.char-btn.selected')?.dataset?.character` — returns `"mermaid-1"` through `"mermaid-9"`.
- **Load failure:** If `mermaid.svg` fetch 404s, `#app` shows `<div class="error">Could not load mermaid.</div>`.
- **Missing character:** Network 404 on `assets/svg/dressup/mermaid-*.svg` when clicking a gallery button means that character's SVG file is missing from `frontend/assets/svg/dressup/`.

## Deviations

**Plan pivot documented:** T03-PLAN.md described running the AI art generation pipeline (gpt-image-1 edit API, vtracer tracing, multi-layer assembly). This work had already been completed and then superseded by the character gallery approach (see commit `39336c0` and WORKLOG.md). The actual T03 work was closing the final gap: aligning the test suite with the implemented CSS hue-rotate recoloring architecture.

**Art generation endpoint noted but not used:** An Azure gpt-image endpoint was provided during execution. Not needed — all 9 character SVGs are already deployed in `frontend/assets/svg/dressup/`.

## Known Issues

None. All 102 tests pass. The dress-up feature is complete with visual verification.

## Files Created/Modified

- `tests/test_dressup.py` — Updated `test_color_swatch_recolors_paths` to assert CSS hue-rotate filter; updated `test_undo_reverts_color` to check filter restoration instead of fill attributes
- `.gsd/milestones/M003/slices/S01/S01-PLAN.md` — Added `## Observability / Diagnostics` section
- `.gsd/milestones/M003/slices/S01/tasks/T03-PLAN.md` — Added `## Steps`, `## Expected Output`, `## Observability Impact` sections
