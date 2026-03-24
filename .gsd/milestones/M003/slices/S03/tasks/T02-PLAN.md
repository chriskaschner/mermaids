---
estimated_steps: 4
estimated_files: 2
skills_used:
  - test
---

# T02: Remove dead pipeline functions from edit.py

**Slice:** S03 — Cleanup & Stability
**Milestone:** M003

## Description

The architecture pivot from multi-layer part-swapping to flat 9-character gallery left dead functions in `edit.py`. `generate_dressup_variants()` references `DRESSUP_VARIANTS` which no longer exists in `prompts.py` — calling it would produce a `NameError`. `composite_all_combinations()` and `generate_base_mermaid()` are only called by `generate_dressup_variants()`. `_CATEGORY_TO_REGION` is only used by `generate_dressup_variants()`. All four must be removed.

The live functions to **keep** are: `create_region_mask()`, `edit_region()`, `REGIONS`, `_get_client()`, and the imports they depend on.

**Pre-verified:** `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid" scripts/ tests/` returns nothing — no external code calls these functions. `_CATEGORY_TO_REGION` also has no external references.

## Steps

1. Open `src/mermaids/pipeline/edit.py` and delete the following:
   - `_CATEGORY_TO_REGION` dict (around line 55-60)
   - `generate_base_mermaid()` function (starts ~line 160)
   - `generate_dressup_variants()` function (starts ~line 175)
   - `composite_all_combinations()` function (starts ~line 218)
   Also remove the `import itertools` inside `composite_all_combinations` — it's a local import that goes away with the function.

2. Update the module docstring (lines 1-5) to describe only the remaining live functionality. Replace references to `generate_dressup_variants()` with a description of `create_region_mask()` and `edit_region()` only.

3. In `tests/test_masks.py` line 116, update the comment `# Character prompt tests (replaces DRESSUP_VARIANTS tests)` to remove the stale `DRESSUP_VARIANTS` reference. Change to something like `# Character prompt tests`.

4. Run verification: `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` must return nothing. Then `uv run pytest -q` must show 103+ passed.

## Must-Haves

- [ ] `generate_dressup_variants()` removed from edit.py
- [ ] `composite_all_combinations()` removed from edit.py
- [ ] `generate_base_mermaid()` removed from edit.py
- [ ] `_CATEGORY_TO_REGION` removed from edit.py
- [ ] Module docstring updated to reflect remaining functions only
- [ ] test_masks.py line 116 comment updated (no "DRESSUP_VARIANTS" reference)
- [ ] No references to removed symbols in src/, scripts/, or tests/
- [ ] Full test suite passes at 103+

## Verification

- `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` → no output (exit code 1)
- `uv run pytest -q` → 103+ passed, 0 failed

## Observability Impact

- Signals added/changed: Removal of dead code eliminates a latent `NameError` trap — `generate_dressup_variants()` referenced the non-existent `DRESSUP_VARIANTS` symbol. After removal, `grep -rn "generate_dressup_variants\|composite_all_combinations\|generate_base_mermaid\|_CATEGORY_TO_REGION" src/ scripts/ tests/` returns nothing, confirming clean codebase.
- How a future agent inspects this: Run `grep -rn "generate_dressup_variants" src/` — exit code 1 confirms the dead code is gone. `uv run pytest -q` confirms no tests depended on removed functions.
- Failure state exposed: If any removed function were still referenced, `uv run pytest` would fail with `ImportError` or `NameError` — making the regression immediately visible.

## Inputs

- `src/mermaids/pipeline/edit.py` — contains the four dead symbols to remove
- `tests/test_masks.py` — contains a stale comment referencing DRESSUP_VARIANTS on line 116

## Expected Output

- `src/mermaids/pipeline/edit.py` — modified: dead functions and dict removed, docstring updated
- `tests/test_masks.py` — modified: stale comment updated
