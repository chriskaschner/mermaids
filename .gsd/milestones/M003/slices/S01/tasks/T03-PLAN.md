# T03: 08-dress-up-art-rework 03

**Slice:** S01 — **Milestone:** M003

## Description

Delete old dress-up assets, run the updated pipeline to generate a fresh base mermaid + 12 isolated part variants, trace to SVG, assemble the multi-layer mermaid.svg, and deploy to frontend. Visual verification by user on real device.

Purpose: The pipeline code (Plan 01) and frontend code (Plan 02) are ready but the app still has old single-character SVG assets. This plan generates the actual AI art, assembles it, deploys it, and gets user visual approval.

Output: New mermaid.svg with multi-layer structure, 12 preview thumbnails, working dress-up on live site.

## Steps

1. **Audit current state** — read git log, current dressup.js/app.js, and test results to establish the actual pipeline design (gallery vs. part-swap).
2. **Fix failing test** — `test_color_swatch_recolors_paths` checked for fill-attribute manipulation but recoloring uses CSS hue-rotate filter. Update test to assert `hue-rotate` filter on `#mermaid-svg`.
3. **Update `test_undo_reverts_color`** — old version read `path[fill]` attributes (unchanged by hue-rotate). Update to assert filter is removed after undo.
4. **Verify local server** — start `python -m http.server 8080 --directory frontend`, open `#/dressup`, visually confirm gallery, swapping, and recoloring on multiple characters including dark-skinned mermaid-4.
5. **Run full test suite** — `uv run pytest` — all 102 tests must pass.
6. **Add observability** — add `## Observability / Diagnostics` to S01-PLAN.md with failure signals.
7. **Write T03-SUMMARY.md** and mark T03 done.

## Expected Output

- `tests/test_dressup.py` — updated to test CSS hue-rotate filter (not fill manipulation)
- `frontend/assets/svg/dressup/mermaid-1.svg` through `mermaid-9.svg` — 9 AI-generated character SVGs deployed
- `frontend/assets/svg/mermaid.svg` — default mermaid (mermaid-1) serving as initial display

## Observability Impact

- **Recolor signal:** `document.getElementById('mermaid-svg')?.style?.filter` returns `hue-rotate(Xdeg)` after swatch click; empty string = no recolor applied. Previously this was tested via `path[fill]` attribute reads — now observable via CSS filter.
- **Character state:** `document.querySelector('.char-btn.selected')?.dataset?.character` gives active character ID.
- **Failure surface:** Network 404 on `assets/svg/dressup/mermaid-*.svg` means character file missing; `#app .error` div appears if `mermaid.svg` fetch fails.
- **Test coverage:** `uv run pytest tests/test_dressup.py -v` — 14 tests covering all observable behaviors. All 102 suite tests provide regression coverage.



- [ ] "User sees one consistent base mermaid body in the dress-up view"
- [ ] "Swapping hair shows different hair on the same body"
- [ ] "Swapping eyes shows different eyes on the same body"
- [ ] "Swapping tail shows different tail on the same body"
- [ ] "Hair and tail regions do not visually overlap"

## Files

- `assets/generated/png/dressup/base/mermaid-base.png`
- `assets/generated/png/dressup/parts/*.png`
- `assets/generated/svg/dressup/*.svg`
- `frontend/assets/svg/mermaid.svg`
- `frontend/assets/svg/dressup/*.svg`
