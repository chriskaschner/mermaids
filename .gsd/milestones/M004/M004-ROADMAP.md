# M004: Dress-Up to Coloring Pipeline

**Vision:** Connect dress-up and coloring into one creative flow — the mermaid you build is the mermaid you color. Fix the open hair SVG paths that cause hue-rotate to recolor non-hair areas. Refresh icons to be semantically meaningful, and fix the remaining blank coloring pages.

## Success Criteria

- Kid can tap "Color This!" in dress-up and land on a coloring canvas with the active character's B&W outline
- All 9 coloring gallery pages show real mermaid art (no blank tiles)
- All icons in the nav bar and home screen visually represent their activity
- Hair SVG paths in all 9 dress-up characters are clipped/redrawn to the visible hair region — hue-rotate no longer recolors body/skin/tail
- 104+ tests passing

## Key Risks / Unknowns

- AI-generated B&W outlines for dress-up characters may not produce clean flood-fillable shapes — existing coloring pages were purpose-prompted, dress-up characters were not
- Outlines must look recognizably like "the same mermaid" — kawaii full-color vs B&W simplification may feel disconnected
- Pages 5-9 art generation requires OpenAI API key and output quality is uncertain
- Hair path clipping/redrawing must preserve visual appearance of hair while removing geometry that extends behind body/tail — automated clipping may leave artifacts that need manual SVG cleanup

## Proof Strategy

- AI outline quality → retire in S01 by generating one character outline and verifying it loads on the coloring canvas with recognizable character features
- Hair path fix → retire in S01 by clipping/redrawing hair paths and verifying hue-rotate only affects the visible hair region, not body/skin/tail
- Pages 5-9 art quality → retire in S03 by running pipeline and verifying all 9 gallery thumbnails show real art

## Verification Classes

- Contract verification: Playwright E2E tests for "Color This!" flow, asset existence tests, icon assertion tests
- Integration verification: Browser verification of full dress-up → coloring flow with real SVG assets
- Operational verification: Deployed to GitHub Pages and coloring pages load on live site
- UAT / human verification: Visual check that outlines look like the dress-up characters, icons are intuitive

## Milestone Definition of Done

This milestone is complete only when all are true:

- "Color This!" button in dress-up navigates to coloring with matching character outline
- 9 dressup-character coloring outlines exist as SVG assets and load correctly
- Hair SVG paths in all 9 dress-up characters are bounded to the visible hair region — hue-rotate recoloring no longer bleeds into body/skin/tail
- All 9 coloring gallery pages show real mermaid art
- All icons across nav bar and home screen are semantically meaningful
- 104+ tests passing
- Deployed to GitHub Pages

## Requirement Coverage

- Covers: PIPE-01, PIPE-02, PIPE-03, ICON-01, COLR-04, HAIR-01
- Partially covers: COLR-02, COLR-03 (visual verification of generated outlines)
- Leaves for later: SCENE-01, ANIM-01
- Orphan risks: none

## Slices

- [x] **S01: Dress-Up → Coloring Pipeline + Hair Path Fix** `risk:high` `depends:[]`
  > After this: Kid picks mermaid-3 in dress-up, taps "Color This!", lands on coloring canvas with mermaid-3's B&W outline loaded and ready to paint. Hair hue-rotate recoloring no longer bleeds into body/skin/tail areas.

- [x] **S02: Icon Refresh** `risk:low` `depends:[]`
  > After this: All nav bar and home screen icons are semantically meaningful — mermaid tail for dress-up, palette for coloring, house for home.

- [x] **S03: Coloring Page Art Fix** `risk:medium` `depends:[]`
  > After this: All 9 coloring gallery pages show real mermaid art (pages 5-9 no longer blank).

## Boundary Map

### S01 (standalone)

Produces:
- `frontend/assets/svg/dressup/mermaid-{1-9}.svg` — 9 dress-up character SVGs with hair paths clipped/redrawn to visible hair region (~y 0-290)
- `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` — 9 B&W outline SVGs matching dress-up characters
- `frontend/js/app.js` — "Color This!" button in renderDressUp(), new route handler or parameter for #/coloring?character=mermaid-3
- `frontend/js/dressup.js` — exports state.activeCharacter (already exists, consumed by app.js)
- E2E test: test_dressup_to_coloring_flow
- E2E test or visual assertion: hair hue-rotate does not recolor body/skin/tail

Consumes:
- `frontend/js/coloring.js` — initColoringCanvas(svgUrl, container) (existing API, unchanged)
- `frontend/js/dressup.js` — state.activeCharacter (existing state, unchanged)
- `src/mermaids/pipeline/prompts.py` — DRESSUP_CHARACTERS for outline generation prompts

### S02 (standalone)

Produces:
- `frontend/js/app.js` — Updated inline SVG icons in renderHome() and renderDressUp()
- `frontend/index.html` — Updated nav bar SVG icons
- E2E test or visual assertion: icons are present and distinct

Consumes:
- nothing (standalone cosmetic slice)

### S03 (standalone)

Produces:
- `frontend/assets/svg/coloring/page-{5-9}*.svg` — 5 real coloring page SVGs (replacing 170-byte empty shells)
- E2E test: all 9 gallery thumbnails render with visible art

Consumes:
- `src/mermaids/pipeline/prompts.py` — COLORING_PAGES entries for pages 5-9 (already defined)
- `scripts/generate_coloring.py` + `scripts/trace_all.py` (existing pipeline)
