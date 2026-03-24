# Mermaid Create & Play

## What This Is

A web-based creative activity app for a 6-year-old, themed entirely around mermaids. Two activities: dress-up (mix and match AI-generated kawaii mermaid characters with color customization) and coloring (canvas flood-fill on AI-generated mermaid pages with crisp SVG overlays). Live at mermaids.chriskaschner.com, designed for iPad Safari with 60pt+ touch targets and zero-instruction usability.

## Core Value

A 6-year-old can open this on an iPad, build her own mermaid, and color mermaid pages — with zero friction and pure delight.

## Current State

Four milestones shipped (M001 MVP, M002 Art & Deploy, M003 Art Rework, M004 Dress-Up to Coloring Pipeline). 116 tests (98 non-E2E + 18 Playwright E2E). Two complete activities connected in a creative loop: dress-up (9 diverse AI-generated kawaii mermaids, gallery swap, CSS hue-rotate recoloring isolated to hair via #hair-group) → coloring (9 pages with real art, canvas flood-fill + brush painting, undo). "Color This!" button in dress-up navigates to coloring canvas with matching character outline. All nav bar and home screen icons are semantically meaningful (mermaid tail for dress-up, pencil for coloring, house for home). Hair recoloring no longer bleeds into body/skin/tail. All 9 coloring gallery pages show real mermaid art. Deployed to GitHub Pages via CI with E2E test gate. Vanilla JS frontend (~1,700 LOC), Python pipeline for AI art generation.

## Architecture / Key Patterns

- **Frontend:** Vanilla JS, no framework, no build step. Hash-based SPA router (#/home, #/dressup, #/coloring). ES modules with cache-busting version params.
- **Art Pipeline:** Python — OpenAI gpt-image-1 API generates PNGs, vtracer converts to SVGs. prompts.py defines page/character metadata, edit.py handles region masks, generate.py orchestrates.
- **Rendering:** SVG-first for dress-up (full character SVGs swapped via innerHTML). Canvas+SVG hybrid for coloring (canvas for flood-fill/brush, SVG overlay for crisp lines).
- **Deployment:** GitHub Pages, static frontend/ directory. CI runs Playwright E2E tests on webkit+chromium before deploy.
- **State:** Module-level JS state objects (no store/framework). Undo via stack (ImageData snapshots for coloring, closure callbacks for dress-up).

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: MVP — Initial app with basic dress-up and coloring
- [x] M002: Art & Deploy — AI art pipeline and GitHub Pages deployment
- [x] M003: Mermaid Art Rework — 9-character gallery, coloring variety, cleanup
- [x] M004: Dress-Up to Coloring Pipeline — Connect dress-up output to coloring input, fix open hair SVG paths, icon refresh, art fixes
