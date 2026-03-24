---
estimated_steps: 4
estimated_files: 5
skills_used:
  - test
---

# T02: Create coloring outline assets for all 9 dress-up characters

**Slice:** S01 — Dress-Up → Coloring Pipeline + Hair Path Fix
**Milestone:** M004

## Description

The "Color This!" flow (T03) needs B&W outline SVGs for each dress-up character. Per decision D002, these are pre-generated static assets — no runtime AI generation. This task creates the generation script and deploys 9 outline SVGs to `frontend/assets/svg/dressup-coloring/`.

The generation script uses the existing AI pipeline pattern: `COLORING_BASE_PROMPT + DRESSUP_CHARACTERS[i]['prompt_detail']` → generate PNG via gpt-image-1 → trace to SVG via vtracer. However, if no OpenAI API key is available, the executor should create clean placeholder B&W mermaid outline SVGs (simple black outlines on white background, 1024x1024 viewBox) that serve as valid coloring targets. The placeholders must be functional — they must load on a canvas and accept flood-fill.

The existing project already has `scripts/generate_coloring.py` and `scripts/trace_all.py` as references for the pipeline pattern.

## Steps

1. **Read the existing pipeline scripts** to understand the generation pattern:
   - `scripts/generate_coloring.py` — how it uses `COLORING_BASE_PROMPT` + page prompt_detail
   - `scripts/trace_all.py` — how it traces PNGs to SVGs with vtracer
   - `src/mermaids/pipeline/prompts.py` — `DRESSUP_CHARACTERS` list (9 entries with `id` and `prompt_detail`)

2. **Create `scripts/generate_dressup_outlines.py`**: Script that generates 9 B&W outline SVGs for the dress-up characters. Pattern: for each character in `DRESSUP_CHARACTERS`, construct prompt = `COLORING_BASE_PROMPT + character['prompt_detail']`, generate via `openai.images.generate()`, trace with vtracer, save to `frontend/assets/svg/dressup-coloring/{character['id']}-outline.svg`. Include `--dry-run` flag that shows what would be generated without calling the API.

3. **Create 9 outline SVGs** in `frontend/assets/svg/dressup-coloring/`: If an OpenAI API key is available (check `OPENAI_API_KEY` env var), run the generation script. If not, create 9 clean placeholder SVGs. Each placeholder should be a valid 1024x1024 SVG with simple B&W mermaid outline shapes (black `stroke`, white `fill`, `stroke-width="3"`). Each must be distinct enough to tell apart (different hair, different tail shape). The key requirement: they must be valid SVGs that load into an `<img>` tag and render on a canvas.

4. **Add asset existence tests** to `tests/test_pipeline.py`: Add a test `test_dressup_coloring_outlines_exist` that verifies all 9 `frontend/assets/svg/dressup-coloring/mermaid-{1-9}-outline.svg` files exist and are each larger than 500 bytes. Add a test `test_dressup_coloring_outlines_are_valid_svg` that opens each file and verifies it starts with `<svg` and contains `viewBox`.

## Must-Haves

- [ ] `scripts/generate_dressup_outlines.py` exists and is runnable
- [ ] All 9 `mermaid-{1-9}-outline.svg` files exist in `frontend/assets/svg/dressup-coloring/`
- [ ] Each outline SVG is a valid SVG (starts with `<svg`, has `viewBox`, >500 bytes)
- [ ] Asset existence and validity tests pass in `tests/test_pipeline.py`

## Verification

- `test -f frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` — first outline exists
- `test -f frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` — last outline exists
- `cd /Users/chriskaschner/Documents/GitHub/mermaids/.gsd/worktrees/M004 && .venv/bin/python -m pytest tests/test_pipeline.py -x -q` — pipeline tests pass
- `wc -c < frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` returns >500

## Inputs

- `scripts/generate_coloring.py` — existing generation script to use as pattern
- `scripts/trace_all.py` — existing tracing script to use as pattern
- `src/mermaids/pipeline/prompts.py` — `COLORING_BASE_PROMPT` and `DRESSUP_CHARACTERS` definitions
- `tests/test_pipeline.py` — existing pipeline tests to add new tests alongside

## Expected Output

- `scripts/generate_dressup_outlines.py` — new generation script
- `frontend/assets/svg/dressup-coloring/mermaid-1-outline.svg` — outline for mermaid-1
- `frontend/assets/svg/dressup-coloring/mermaid-2-outline.svg` — outline for mermaid-2
- `frontend/assets/svg/dressup-coloring/mermaid-3-outline.svg` — outline for mermaid-3
- `frontend/assets/svg/dressup-coloring/mermaid-4-outline.svg` — outline for mermaid-4
- `frontend/assets/svg/dressup-coloring/mermaid-5-outline.svg` — outline for mermaid-5
- `frontend/assets/svg/dressup-coloring/mermaid-6-outline.svg` — outline for mermaid-6
- `frontend/assets/svg/dressup-coloring/mermaid-7-outline.svg` — outline for mermaid-7
- `frontend/assets/svg/dressup-coloring/mermaid-8-outline.svg` — outline for mermaid-8
- `frontend/assets/svg/dressup-coloring/mermaid-9-outline.svg` — outline for mermaid-9
- `tests/test_pipeline.py` — updated with outline asset tests
