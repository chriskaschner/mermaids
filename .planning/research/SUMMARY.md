# Research Summary: v1.1 Art & Deploy

**Domain:** Integration of AI art pipeline, flood-fill coloring, and static deployment into existing kids creative web app
**Researched:** 2026-03-09
**Overall confidence:** HIGH

## Executive Summary

The v1.1 milestone adds three capabilities to the existing Mermaid Create & Play app: AI-generated kawaii art (replacing hand-crafted SVGs), canvas-based flood-fill coloring (replacing SVG region-based tap-to-fill), and GitHub Pages deployment (replacing FastAPI-only serving). After thorough analysis of the existing codebase (2,172 LOC, 37 Playwright tests, 5 JS modules, 1 Python pipeline module) and the target features, the integration path is clear but requires careful sequencing.

The biggest architectural change is in coloring. The v1.0 coloring system uses hand-tagged `<g data-region="tail">` SVG groups that get their `fill` attribute changed on tap. This does not work with AI-generated art because traced SVGs produce hundreds of stacked paths with no semantic grouping. The solution is a hybrid canvas+SVG architecture: render line art SVG onto a `<canvas>` for flood-fill pixel operations, overlay the original SVG with `pointer-events: none` to keep line art crisp. This is a well-established pattern (Microsoft's Windows Coloring Book sample app uses the same layered approach).

The dress-up system is architecturally sound for the transition. The `<defs>` + `<use>` variant swap pattern (change `href` attribute to swap parts) works identically regardless of whether the art inside `<defs>` is hand-drawn or AI-generated. The challenge is producing AI art that fits the convention: each variant as a separate generation, spatially aligned, wrapped in `<g id="tail-1">` groups by a post-processing pipeline. The recoloring system (set all fills to one color) maps naturally to kawaii flat-color style.

GitHub Pages deployment is trivial given the existing architecture. Hash routing already works (the browser never sends hash fragments to the server). The only code change is fixing one absolute fetch path in `app.js` (`/assets/svg/mermaid.svg` -> `assets/svg/mermaid.svg`). No build step is needed -- the `frontend/` directory deploys as-is.

The art generation pipeline is the highest-risk component. AI image consistency across separate generations is unreliable. The recommended approach: generate a full reference character, then use OpenAI's edit API with masks to create variants of specific regions (different tails, different hairstyles). Use gpt-image-1 (not DALL-E 3, which is deprecated May 2026). All generation happens offline at dev time; assets are committed as static files.

## Key Findings

**Stack:** Existing stack is correct. Add openai Python package for pipeline, canvas flood-fill in vanilla JS. No new frontend dependencies. gpt-image-1 replaces deprecated DALL-E 3.

**Architecture:** Hybrid canvas+SVG for coloring (biggest change). Dress-up defs+use pattern preserved. Pipeline produces static assets committed to repo. GitHub Pages serves frontend/ directory with zero build step.

**Critical pitfall:** Canvas memory limits on iPad Safari. Must release canvas resources when navigating away from coloring pages. Single shared canvas, never create-per-page.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Art Pipeline** - Build the offline pipeline first (generate.py + trace.py updates + assemble.py)
   - Addresses: AI art generation, kawaii style, SVG asset production
   - Avoids: Building frontend features without assets to test against
   - This phase can be tested with Python unit tests alone, no browser needed

2. **Flood-Fill Coloring Refactor** - Replace SVG region coloring with canvas flood fill
   - Addresses: Coloring pages that work with any AI-generated art
   - Avoids: Manual region tagging (impossible to maintain with AI art)
   - Depends on: Phase 1 for coloring page SVGs to test against
   - Biggest code change: coloring.js rewrite + floodfill.js new module + app.js openColoringPage changes

3. **Dress-Up Art Swap** - Replace hand-crafted mermaid.svg with AI-generated version
   - Addresses: Kawaii art style for dress-up
   - Avoids: Major code changes (mechanism is unchanged, only art and PARTS IDs change)
   - Depends on: Phase 1 for mermaid SVG assets

4. **GitHub Pages Deployment** - Static deployment + path fixes
   - Addresses: Accessibility on iPad (no need to run FastAPI)
   - Avoids: Breaking tests (keep FastAPI for dev/test)
   - Depends on: Phases 2-3 (all features must work before deploying)

**Phase ordering rationale:**
- Pipeline must come first because both coloring and dress-up need the new art assets
- Coloring before dress-up because coloring is the larger architectural change (new module, rewritten module, canvas layer)
- Dress-up after coloring because it is mostly art-swap with minimal code changes
- Deploy last because deploying a broken app is worse than not deploying

**Research flags for phases:**
- Phase 1 (Art Pipeline): Likely needs deeper research on prompt engineering for consistent kawaii style, and on gpt-image-1 edit API with masks for variant generation
- Phase 2 (Flood Fill): Standard patterns, good reference implementations available. The canvas+SVG overlay is well-understood. Tolerance tuning (anti-aliasing handling) may need iteration.
- Phase 3 (Dress-Up): Low risk. The defs+use mechanism is proven. Risk is in art asset quality, not code.
- Phase 4 (Deploy): Standard GitHub Pages setup. No research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack is correct; only addition is openai Python package |
| Features | HIGH | All features are well-understood patterns (flood fill, SVG variants, static deploy) |
| Architecture | HIGH | Direct codebase analysis + established patterns (canvas flood fill, SVG defs+use) |
| Pitfalls | HIGH | Verified against official docs (Apple canvas limits, OpenAI API deprecations, GitHub Pages behavior) |
| Art Pipeline | MEDIUM | AI art consistency is inherently unpredictable; edit API approach is recommended but needs validation |

## Gaps to Address

- **Prompt engineering specifics.** What exact prompts produce consistent kawaii mermaid art with clean outlines suitable for tracing? This requires empirical iteration, not research.
- **gpt-image-1 edit API with masks.** Confirmed available but not deeply tested for the specific use case of "keep this character, regenerate only the tail region." Phase-specific research recommended.
- **vtracer settings for AI art.** The current `simplify=True` binary mode works for hand-drawn art. AI-generated images with more detail may need different `filter_speckle`, `color_precision`, and `layer_difference` values. Empirical tuning needed.
- **Canvas flood-fill performance on older iPads.** The algorithm is fast in theory (~20-50ms for 1024x1024) but real-world performance depends on iPad model. Test on actual hardware early.
