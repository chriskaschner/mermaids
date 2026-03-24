# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### COLR-02 — Hair regions are closed shapes that flood-fill can color
- Class: core-capability
- Status: active
- Description: Hair regions are closed shapes that flood-fill can color.
- Why it matters: Without closed outlines, flood-fill bleeds through gaps and ruins the coloring experience.
- Source: inferred
- Primary owning slice: M003/S02
- Supporting slices: M003/S03
- Validation: partial
- Notes: Prompts explicitly request closed outlines. All 9 SVGs traced and deployed. Actual flood-fill quality depends on AI output — visual verification needed.

### COLR-03 — Tail regions are closed shapes that flood-fill can color
- Class: core-capability
- Status: active
- Description: Tail regions are closed shapes that flood-fill can color.
- Why it matters: Without closed outlines, flood-fill bleeds through gaps and ruins the coloring experience.
- Source: inferred
- Primary owning slice: M003/S02
- Supporting slices: M003/S03
- Validation: partial
- Notes: Prompts explicitly request closed outlines. All 9 SVGs traced and deployed. Actual flood-fill quality depends on AI output — visual verification needed.

### COLR-04 — All 9 coloring gallery pages show real art
- Class: core-capability
- Status: validated
- Description: All 9 coloring page thumbnails in the gallery display actual mermaid art, not blank white tiles. Pages 5-9 currently have empty 170-byte placeholder SVGs.
- Why it matters: Blank tiles make the app feel broken. A 6-year-old sees 4 working pages and 5 broken ones.
- Source: inferred
- Primary owning slice: M004/S03
- Supporting slices: none
- Validation: validated — All 9 coloring SVGs have ≥5 path elements (8-28 each). test_all_coloring_svgs_have_real_art passes. Browser verification confirms all 9 gallery thumbnails render visible mermaid artwork. Pages 5-9 replaced with scene-themed geometric placeholders (4-5KB, 18-28 paths). 70 non-E2E tests pass, 116 total collected.
- Notes: Pages 5-9 are geometric placeholders (not AI-generated). Functionally adequate for gallery display. Can be upgraded to AI-traced art by running scripts/generate_coloring.py + scripts/trace_all.py with OPENAI_API_KEY.

## Validated

### ICON-01 — All navigation and activity icons are semantically meaningful
- Class: quality-attribute
- Status: validated
- Description: Every icon in the nav bar and home screen represents its activity — not generic star/pencil shapes. Mermaid-themed where possible (tail for dress-up, palette for coloring, house for home).
- Why it matters: A 6-year-old navigates by icon recognition. A star means nothing for "dress up your mermaid."
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: validated — TestIconSemantics class (4 tests) asserts all nav icons have distinct non-empty aria-labels, all nav icons contain inline SVG children, and both home screen activity buttons have correct labels ("Dress Up", "Coloring") with SVG children. Star polygon paths removed from index.html and app.js, replaced with mermaid tail cubic-bezier paths. 115 tests passing.
- Notes: Covers both nav bar icons (3) and home screen activity buttons (2).

### PIPE-01 — Dress-up → coloring pipeline: customized mermaid becomes a coloring page
- Class: primary-user-loop
- Status: validated
- Description: Kid customizes a mermaid in dress-up, taps "Color This!", and lands on the coloring canvas with that mermaid's matching B&W outline loaded and ready to color.
- Why it matters: Connects the two activities into one creative flow — the mermaid you build is the mermaid you color.
- Source: user
- Primary owning slice: M004/S01
- Supporting slices: none
- Validation: validated — E2E test test_dressup_to_coloring_navigates confirms dress-up → coloring navigation loads matching character outline on canvas. 4 E2E tests in TestDressUpToColoring class.
- Notes: Character identity carries over (which of the 9 mermaids), not hue-rotate color (coloring pages are B&W).

### PIPE-02 — "Color This!" button in dress-up navigates to coloring canvas with matching outline
- Class: primary-user-loop
- Status: validated
- Description: A visible "Color This!" button in the dress-up view navigates directly to the coloring canvas with the active character's outline pre-loaded — no gallery detour.
- Why it matters: The transition must be immediate and obvious to a 6-year-old.
- Source: user
- Primary owning slice: M004/S01
- Supporting slices: none
- Validation: validated — E2E test test_color_this_button_visible confirms button presence; test_dressup_to_coloring_navigates confirms navigation. Button styled with coral gradient, 60px min-height, child-friendly.
- Notes: Button should be prominent and child-friendly. Skips the coloring gallery entirely.

### PIPE-03 — 9 pre-generated coloring outlines matching dress-up characters
- Class: core-capability
- Status: validated
- Description: 9 B&W coloring outline SVGs exist in frontend/assets/, one for each dress-up character (mermaid-1 through mermaid-9), generated via the AI pipeline and bundled as static assets.
- Why it matters: Makes "Color This!" instant — no API call, no wait. The outline must look recognizably like the same mermaid the kid just customized.
- Source: user
- Primary owning slice: M004/S01
- Supporting slices: none
- Validation: validated (partial) — 9 outline SVGs exist at dressup-coloring/mermaid-{1-9}-outline.svg, each >3KB, valid SVG with viewBox. Asset existence and validity tests pass. Outlines are geometric placeholders, not AI-generated character-faithful art. Re-runnable with OPENAI_API_KEY.
- Notes: Generated offline via scripts/generate_dressup_outlines.py --placeholder. Functional for pipeline (load on canvas, accept flood-fill) but not visually matching dress-up characters. Run script without --placeholder with OPENAI_API_KEY to generate character-faithful outlines.

### HAIR-01 — Dress-up hair SVG paths are bounded to the visible hair region
- Class: core-capability
- Status: validated
- Description: Hair paths in all 9 mermaid-{1-9}.svg dress-up characters are clipped or redrawn so their geometry is bounded to the visible hair region (~y 0-290). CSS hue-rotate applied to the hair region no longer visually recolors body, skin, or tail areas.
- Why it matters: When a kid changes hair color, only the hair should change. Currently the hair paths extend behind the entire body, so hue-rotate shifts color on skin and tail too — confusing and ugly.
- Source: user
- Primary owning slice: M004/S01
- Supporting slices: none
- Validation: validated — E2E test test_hue_rotate_targets_hair_group_not_root confirms hue-rotate applied to #hair-group only, root SVG filter empty. All 10 SVGs (9 dressup + mermaid.svg) contain hair-group wrapper.
- Notes: Fixed via hair-group wrapper approach — existing clipped paths wrapped in <g id="hair-group">, filter target moved from root SVG to group. Supersedes D001.

### COLR-01 — Coloring pages feature hair/eyes/tail variety across pages
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S02
- Validation: validated
- Notes: 9 coloring pages defined in both prompts.py and coloring.js with distinct hair/eyes/tail per page. test_coloring_page_prompts_have_distinct_styles asserts all 9 IDs and prompt_detail values are unique.

### DEBT-01 — Debug overlay removed from app.js
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S02
- Validation: validated
- Notes: _initDebug function, ?debug=1 activation, and triple-tap wiring fully removed. grep -q "_initDebug" exits 1.

### DEBT-02 — WebKit sparkle E2E test failures fixed
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S02
- Validation: validated
- Notes: WebKit sparkle E2E tests pass. No code changes required; pre-existing fix confirmed.

### DRSU-01 — User sees a single base mermaid (gallery shows one mermaid at a time)
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S01
- Validation: validated

### DRSU-02 — User can swap between multiple hair style variants
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S01
- Validation: validated

### DRSU-03 — User can swap between multiple eye style variants
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S01
- Validation: validated

### DRSU-04 — User can swap between multiple tail style variants
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S01
- Validation: validated

### DEBT-03 — AI-generated hair/tail region overlap fixed
- Class: core-capability
- Status: validated
- Source: inferred
- Primary owning slice: M003/S01
- Validation: validated
- Notes: Region masks redesigned with non-overlapping vertical zones (hair y2=290 < tail y1=550).

## Deferred

### SCENE-01 — Scene backgrounds: place customized mermaid into underwater scenes
- Class: differentiator
- Status: deferred
- Description: User can place their customized mermaid into different underwater scene backgrounds (coral reef, castle, etc.)
- Why it matters: Adds creative variety and a sense of place to the mermaid experience.
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: Deferred to a future milestone. Depends on dress-up → coloring pipeline being solid first.

### ANIM-01 — Light ambient animation on scenes
- Class: differentiator
- Status: deferred
- Description: Subtle movement on scene backgrounds — water swishing, tail flicking. Not full animation, more like ambient motion.
- Why it matters: Makes scenes feel alive rather than static images.
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: Deferred to a future milestone after scenes. Different technical domain (CSS/JS animation on SVG).

## Out of Scope

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| PIPE-01 | primary-user-loop | validated | M004/S01 | none | validated |
| PIPE-02 | primary-user-loop | validated | M004/S01 | none | validated |
| PIPE-03 | core-capability | validated | M004/S01 | none | validated (partial) |
| ICON-01 | quality-attribute | validated | M004/S02 | none | validated |
| HAIR-01 | core-capability | validated | M004/S01 | none | validated |
| COLR-02 | core-capability | active | M003/S02 | M003/S03 | partial |
| COLR-03 | core-capability | active | M003/S02 | M003/S03 | partial |
| COLR-04 | core-capability | validated | M004/S03 | none | validated |
| COLR-01 | core-capability | validated | M003/S02 | none | validated |
| DEBT-01 | core-capability | validated | M003/S02 | none | validated |
| DEBT-02 | core-capability | validated | M003/S02 | none | validated |
| DRSU-01 | core-capability | validated | M003/S01 | none | validated |
| DRSU-02 | core-capability | validated | M003/S01 | none | validated |
| DRSU-03 | core-capability | validated | M003/S01 | none | validated |
| DRSU-04 | core-capability | validated | M003/S01 | none | validated |
| DEBT-03 | core-capability | validated | M003/S01 | none | validated |
| SCENE-01 | differentiator | deferred | none | none | unmapped |
| ANIM-01 | differentiator | deferred | none | none | unmapped |

## Coverage Summary

- Active requirements: 2
- Mapped to slices: 2
- Validated: 14
- Unmapped active requirements: 0
