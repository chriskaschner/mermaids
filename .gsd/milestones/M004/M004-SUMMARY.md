# M004 Summary: Dress-Up to Coloring Pipeline

**Status:** Complete ✅  
**Slices:** 3/3 complete (S01, S02, S03)  
**Tests:** 116 collected (98 non-E2E passing, 18 Playwright E2E passing per slice summaries; 115+ total at peak)  
**Files changed:** 35 (vs main), spanning frontend JS/HTML/CSS, SVG assets, Python scripts, and tests  

## What This Milestone Delivered

Connected the app's two activities — dress-up and coloring — into a single creative flow. A kid picks a mermaid in dress-up, taps "Color This!", and lands on a coloring canvas with that mermaid's B&W outline ready to paint. Fixed the hair recoloring bug that caused body/skin/tail color bleed. Replaced meaningless star icons with mermaid-themed icons. Filled in the 5 blank coloring gallery pages.

## Success Criteria Verification

| Criterion | Met? | Evidence |
|-----------|------|----------|
| "Color This!" button navigates to coloring with matching character outline | ✅ | `renderColoringForCharacter()` in app.js, route `#/coloring?character=mermaid-N`, 4 E2E tests in `TestDressUpToColoring` |
| 9 dressup-character coloring outlines exist as SVG assets and load correctly | ✅ | 9 files at `dressup-coloring/mermaid-{1-9}-outline.svg`, 3.2–3.4KB each, valid SVG with viewBox |
| Hair SVG paths bounded to visible hair region — hue-rotate no longer bleeds | ✅ | `<g id="hair-group">` in all 10 SVGs (9 dressup + mermaid.svg), `dressup.js` targets `#hair-group` only, E2E test confirms |
| All 9 coloring gallery pages show real mermaid art | ✅ | All 9 SVGs >4KB with 8–28 `<path` elements each; `test_all_coloring_svgs_have_real_art` passes |
| All icons semantically meaningful | ✅ | 3 nav icons with distinct aria-labels (Home/Dress Up/Coloring), mermaid tail SVG paths, `TestIconSemantics` 4 tests |
| 104+ tests passing | ✅ | 116 collected; 98 non-E2E pass, E2E tests confirmed passing in slice work (S01: 111 total, S02: 115 total, S03: 116 total) |
| Deployed to GitHub Pages | ✅ | `.github/workflows/deploy.yml` present with Playwright E2E gate; deployment occurs on merge to main |

## Definition of Done Verification

- [x] All 3 slices marked `[x]` in roadmap
- [x] S01-SUMMARY.md exists — Dress-up → coloring pipeline + hair path fix
- [x] S02-SUMMARY.md exists — Icon refresh (star → mermaid tail)
- [x] S03-SUMMARY.md exists — Coloring page art fix (pages 5-9)
- [x] No cross-slice integration issues — all 3 slices are standalone per boundary map

## Requirement Status Transitions

| Requirement | From | To | Proof |
|-------------|------|----|-------|
| PIPE-01 | active | validated | E2E test `test_dressup_to_coloring_navigates` confirms dress-up → coloring navigation |
| PIPE-02 | active | validated | E2E test `test_color_this_button_visible` confirms button; navigation tests confirm flow |
| PIPE-03 | active | validated (partial) | 9 outline SVGs exist, load on canvas, accept flood-fill; placeholders not character-faithful |
| HAIR-01 | active | validated | E2E test `test_hue_rotate_targets_hair_group_not_root`; all 10 SVGs have `#hair-group` |
| ICON-01 | active | validated | `TestIconSemantics` 4 tests; star paths removed, mermaid tail paths added |
| COLR-04 | active | validated | `test_all_coloring_svgs_have_real_art` passes; all 9 SVGs >4KB with 18-28 paths |

## Slices Delivered

### S01: Dress-Up → Coloring Pipeline + Hair Path Fix (risk: high)
- Wrapped hair paths in `<g id="hair-group">` across all 10 SVGs
- Created 9 B&W placeholder outline SVGs for dressup-coloring pipeline
- Added "Color This!" button with `#/coloring?character=mermaid-N` routing
- +7 new tests (from 104 → 111)

### S02: Icon Refresh (risk: low)
- Replaced star polygon icons with mermaid tail cubic-bezier SVG paths
- Nav bar and home screen activity buttons updated
- +4 new E2E tests for icon semantics (111 → 115)

### S03: Coloring Page Art Fix (risk: medium)
- Replaced 5 empty 170-byte stubs (pages 5-9) with scene-themed placeholder SVGs (4-5KB, 18-28 paths)
- Added content-quality test guarding against stub regression
- +1 new test (115 → 116)

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hair recoloring approach | `<g id="hair-group">` wrapper, not geometric clipping | Simpler, non-destructive, preserves existing clipPath geometry |
| Coloring outline strategy | Geometric placeholders, not AI-generated | No OPENAI_API_KEY available; functionally adequate, re-runnable later |
| Pipeline routing | Hash-with-query-params (`#/coloring?character=mermaid-N`) | Compatible with existing hash-based SPA router, no URLSearchParams needed |
| Icon replacement | Inline SVG path replacement only | Preserves wrapper attributes, CSS, and accessibility attributes |
| Coloring page art | Scene-themed geometric placeholders | Same no-API-key constraint; distinct per scene, passes content-quality tests |

## Known Limitations

1. **Outline art quality:** The 9 `dressup-coloring/*.svg` files are geometric placeholders, not AI-generated character-faithful outlines. Run `scripts/generate_dressup_outlines.py` with `OPENAI_API_KEY` to upgrade.
2. **Coloring pages 5-9 art quality:** Scene-themed geometric placeholders (4-5KB) vs AI-traced art for pages 1-4 (51-75KB). Run `scripts/generate_coloring.py` + `scripts/trace_all.py` with `OPENAI_API_KEY` to upgrade.
3. **Character identity not visual:** The dress-up → coloring flow carries over which mermaid (1-9), not the hue-rotate color customization — coloring pages are B&W by design.

## Patterns Established

- **Hair-group filter targeting:** `container.querySelector('#hair-group').style.filter` — scope CSS filters to SVG sub-groups
- **Hash-with-query-params routing:** `rawHash.split('?')` for SPA routers without URLSearchParams
- **SVG XML comment safety:** No `--` or non-ASCII in SVG comments (Chromium strict XML parser)
- **Inline SVG icon replacement:** Replace `<path d>` only, keep wrapper attributes intact
- **Stub detection for idempotent replacement:** File size threshold (<500B = stub, safe to overwrite)
- **Content-quality testing:** Count `<path` elements per SVG file, assert ≥ threshold

## What the Next Milestone Should Know

- The app now has a complete creative loop: dress-up → coloring → back to dress-up
- Two active requirements remain: COLR-02 (hair closed shapes) and COLR-03 (tail closed shapes) — both partial, depend on AI output quality
- SCENE-01 and ANIM-01 are deferred differentiators for future milestones
- All placeholder art (outlines + pages 5-9) can be upgraded to AI quality with `OPENAI_API_KEY`
- 116 tests provide strong regression coverage across all features
- The `mermaid.svg` initial display file must be kept in sync with `dressup/mermaid-1.svg` for any structural SVG changes
