---
id: T02
parent: S01
milestone: M004
provides:
  - 9 B&W placeholder outline SVGs at frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg
  - scripts/generate_dressup_outlines.py — runnable AI pipeline script with --dry-run and --placeholder flags
  - 2 new asset tests in tests/test_pipeline.py (existence + valid-SVG checks)
key_files:
  - scripts/generate_dressup_outlines.py
  - frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-2-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-3-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-4-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-5-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-6-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-7-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-8-outline.svg
  - frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg
  - tests/test_pipeline.py
key_decisions:
  - No OPENAI_API_KEY available; created placeholder SVGs instead of AI-generated ones — valid coloring targets (white fill, black stroke, 1024x1024 viewBox)
  - Each placeholder has distinct shape data (_CHARACTER_SHAPES dict keyed by char id) so characters are visually identifiable
  - --dry-run flag does not require OPENAI_API_KEY (API key check is skipped in dry-run path)
patterns_established:
  - scripts/generate_dressup_outlines.py pattern: --placeholder for static SVG output, --dry-run to preview AI prompts, bare invocation for full AI pipeline (requires OPENAI_API_KEY)
  - Placeholder SVG structure: white rect background + body/head/hair/tail/fins all with fill="white" stroke="#000" — flood-fill compatible because all regions are closed white shapes bounded by black outlines
  - Test pattern for static asset existence: iterate OUTLINE_IDS list, check path.exists() + stat().st_size > 500; validity: read_text() startswith '<svg' + 'viewBox' in content
observability_surfaces:
  - scripts/generate_dressup_outlines.py --dry-run prints prompt per character without API call — useful to inspect which prompt would be sent
  - scripts/generate_dressup_outlines.py exits with code 1 and writes to stderr on EnvironmentError (missing API key)
  - pytest tests/test_pipeline.py::test_dressup_coloring_outlines_exist — pass means all 9 files present and >500 bytes; fail shows which filenames are missing
  - pytest tests/test_pipeline.py::test_dressup_coloring_outlines_are_valid_svg — pass means each file is a valid SVG; fail shows which files lack <svg or viewBox
duration: ~25m
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T02: Create coloring outline assets for all 9 dress-up characters

**Created 9 B&W placeholder SVGs in `frontend/assets/svg/dressup-coloring/` and a runnable `scripts/generate_dressup_outlines.py` generation script; added 2 asset existence/validity tests to `tests/test_pipeline.py`.**

## What Happened

No `OPENAI_API_KEY` was available, so the task took the placeholder path: each of the 9 dress-up characters gets a dedicated B&W SVG with a recognizable chibi-mermaid outline (head, eyes, hair, body, tail, fins, accessory). Every shape uses `fill="white" stroke="#000" stroke-width="3"` — this makes them valid flood-fill targets: the canvas flood-fill algorithm will fill the white interior up to the black boundary without bleeding into neighbouring regions.

**Shape distinctiveness:** A `_CHARACTER_SHAPES` dict in the script maps each `mermaid-{id}` to unique path data for hair, tail, fins, and an accessory. For example, mermaid-1 has long wavy hair and rounded tail fins; mermaid-5 has two afro-puff ellipses for hair with a star-shaped tail; mermaid-9 has a short bob with a seashell clip.

**Generation script (`scripts/generate_dressup_outlines.py`):**
- `--placeholder`: creates the geometric SVGs, no API call (what was run here)
- `--dry-run`: shows prompt strings that would be sent per character, no API call
- bare invocation: full AI pipeline — calls `generate_image()` + `trace_to_svg()` per character; exits with code 1 and stderr message if `OPENAI_API_KEY` is unset

**Test additions to `tests/test_pipeline.py`:**
- `test_dressup_coloring_outlines_exist`: asserts all 9 files exist and each > 500 bytes; reports all missing/small files in one failure message
- `test_dressup_coloring_outlines_are_valid_svg`: reads each file, checks `startswith('<svg')` and `'viewBox' in content`; reports all failures in one message

**Bug fix during implementation:** The initial `--dry-run` implementation still ran the `OPENAI_API_KEY` check and raised `EnvironmentError` before printing anything useful. Fixed by moving the key check inside the `if not dry_run:` branch so `--dry-run` works without credentials.

## Verification

All four task must-haves confirmed:

1. `scripts/generate_dressup_outlines.py` exists and is runnable (`--placeholder`, `--dry-run` both work)
2. All 9 `mermaid-{1-9}-outline.svg` files present in `frontend/assets/svg/dressup-coloring/`
3. Each file starts with `<svg`, contains `viewBox`, and is >500 bytes (3,300–3,525 bytes each)
4. Both new asset tests pass; full pipeline test suite passes (7 tests)

Also confirmed: `tests/test_dressup.py` still passes (15 tests) — no regressions from the T01 work.

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `.venv/bin/python scripts/generate_dressup_outlines.py --placeholder` | 0 | ✅ pass | <5s |
| 2 | `test -f frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` | 0 | ✅ pass | <1s |
| 3 | `test -f frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` | 0 | ✅ pass | <1s |
| 4 | `wc -c < frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` (returns 3445) | 0 | ✅ pass | <1s |
| 5 | `.venv/bin/python -m pytest tests/test_pipeline.py -x -q` (7 passed) | 0 | ✅ pass | 0.76s |
| 6 | `.venv/bin/python -m pytest tests/test_dressup.py -x -q` (15 passed) | 0 | ✅ pass | 9.1s |
| 7 | `grep -l 'viewBox' frontend/assets/svg/dressup-coloring/*.svg \| wc -l` (returns 9) | 0 | ✅ pass | <1s |
| 8 | `.venv/bin/python scripts/generate_dressup_outlines.py --dry-run` | 0 | ✅ pass | <2s |

## Diagnostics

- **Inspect generated SVG:** `head -5 frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` — should show `<svg ... viewBox="0 0 1024 1024">`
- **Verify all 9 files and sizes:** `wc -c frontend/assets/svg/dressup-coloring/*.svg` — all should be >500 bytes
- **Check flood-fill compatibility:** open SVG in browser, verify all closed shapes have `fill="white"` and `stroke="#000"` — flood-fill will only fill white interiors
- **Preview AI prompts:** `python scripts/generate_dressup_outlines.py --dry-run` — shows the exact prompt string per character without any API call
- **Missing-key error shape:** running without `--placeholder` and without `OPENAI_API_KEY` prints `Error: OPENAI_API_KEY is not set...` to stderr and exits with code 1

## Deviations

**`--dry-run` initially required API key:** The first implementation raised `EnvironmentError` even in dry-run mode. Fixed by moving the key check inside `if not dry_run:` — dry-run now works without credentials.

**No AI generation:** OPENAI_API_KEY unavailable, so placeholder SVGs were created instead of AI-generated ones. The script structure is identical to what a future run with an API key would use — the placeholder SVGs can be replaced by running `python scripts/generate_dressup_outlines.py` (with the key set) which will skip already-existing files unless they are deleted first.

## Known Issues

**Placeholder art is geometric, not character-faithful:** The placeholders are recognizably mermaid-shaped and distinct per character, but they don't visually match the corresponding colored dress-up SVGs (mermaid-1.svg etc.). A future run of the script with `OPENAI_API_KEY` set (after deleting the placeholders) will replace them with AI-generated outlines that match the dress-up characters more closely. This is expected per the plan ("placeholders must be functional — they must load on a canvas and accept flood-fill").

## Files Created/Modified

- `scripts/generate_dressup_outlines.py` — new generation script with --placeholder, --dry-run, and AI pipeline modes
- `frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` — B&W placeholder outline SVG (3,445 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-2-outline.svg` — B&W placeholder outline SVG (3,524 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-3-outline.svg` — B&W placeholder outline SVG (3,486 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-4-outline.svg` — B&W placeholder outline SVG (3,328 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-5-outline.svg` — B&W placeholder outline SVG (3,454 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-6-outline.svg` — B&W placeholder outline SVG (3,451 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-7-outline.svg` — B&W placeholder outline SVG (3,483 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-8-outline.svg` — B&W placeholder outline SVG (3,503 bytes)
- `frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` — B&W placeholder outline SVG (3,400 bytes)
- `tests/test_pipeline.py` — added test_dressup_coloring_outlines_exist and test_dressup_coloring_outlines_are_valid_svg
