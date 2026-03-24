---
id: T02
parent: S03
milestone: M003
provides:
  - Dead pipeline functions and dict removed from edit.py; zero grep hits for removed symbols across src/, scripts/, tests/
key_files:
  - src/mermaids/pipeline/edit.py
  - tests/test_masks.py
key_decisions:
  - Also removed unused imports (generate_image, GENERATED_PNG_DIR, RETRY_BASE_DELAY, RETRY_MAX) that were only needed by the deleted functions — leaving the module minimal
patterns_established:
  - When deleting dead functions, also audit and remove imports that become orphaned to prevent false lint-clean illusions
observability_surfaces:
  - "grep -rn \"generate_dressup_variants|composite_all_combinations|generate_base_mermaid|_CATEGORY_TO_REGION\" src/ scripts/ tests/ --include=\"*.py\" → exit code 1 confirms dead code is gone; uv run pytest -q → 103 passed confirms no tests depended on removed functions"
duration: ~5min
verification_result: passed
completed_at: 2026-03-23
blocker_discovered: false
---

# T02: Remove dead pipeline functions from edit.py

**Deleted four dead symbols (`generate_dressup_variants`, `composite_all_combinations`, `generate_base_mermaid`, `_CATEGORY_TO_REGION`) and their orphaned imports from edit.py, eliminating a latent NameError trap from the architecture pivot.**

## What Happened

After the architecture pivot from multi-layer part-swapping to flat 9-character gallery, `edit.py` retained three functions and a dict that referenced `DRESSUP_VARIANTS` — a symbol that no longer exists in `prompts.py`. Any call to `generate_dressup_variants()` would crash with `NameError: name 'DRESSUP_VARIANTS' is not defined`.

Pre-verified that no external callers existed (`grep --include="*.py"` across src/, scripts/, tests/ returned no external references).

Applied four surgical edits:

1. **Module docstring** — rewrote to describe only `create_region_mask()` and `edit_region()`, removing reference to `generate_dressup_variants()` and the 12-variant generation pipeline.

2. **`_CATEGORY_TO_REGION` dict** (lines 55–61) — deleted entirely.

3. **`generate_base_mermaid()`, `generate_dressup_variants()`, `composite_all_combinations()`** — deleted all three functions from the end of the file. The `import itertools` local import inside `composite_all_combinations` was removed with it.

4. **Orphaned imports** — removed `generate_image`, `GENERATED_PNG_DIR`, `RETRY_BASE_DELAY`, `RETRY_MAX` from the import block. These were exclusively used by the deleted functions. `retry_api_call` was kept — it is still used by `edit_region()`.

5. **`tests/test_masks.py`** — updated the section comment `# Character prompt tests (replaces DRESSUP_VARIANTS tests)` to `# Character prompt tests`, removing the stale `DRESSUP_VARIANTS` reference.

## Verification

- `grep --include="*.py" -rn "generate_dressup_variants|composite_all_combinations|generate_base_mermaid|_CATEGORY_TO_REGION" src/ scripts/ tests/` → exit code 1 (no matches) ✅
- `uv run pytest -q` → 103 passed, 0 failed ✅

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `grep --include="*.py" -rn "generate_dressup_variants\|...\|_CATEGORY_TO_REGION" src/ scripts/ tests/` | 1 (no output) | ✅ pass | <1s |
| 2 | `uv run pytest -q` | 0 | ✅ pass | 50.3s |

## Diagnostics

- **Dead-code sentinel:** `grep --include="*.py" -rn "generate_dressup_variants" src/` → exit code 1 confirms removal. If the symbol reappears, `uv run pytest` fails with `NameError` at import time, making the regression immediately visible.
- **Import cleanliness:** `python -c "import mermaids.pipeline.edit"` succeeds without warning — no unused imports remain.
- Note: `src/mermaids/pipeline/__pycache__/edit.cpython-311.pyc` binary still matches on a grep without `--include="*.py"`, but this is a stale cached bytecode and is regenerated on next import. Always use `--include="*.py"` for source-clean verification.

## Deviations

Minor: also removed four orphaned imports (`generate_image`, `GENERATED_PNG_DIR`, `RETRY_BASE_DELAY`, `RETRY_MAX`) that were not called out in the task plan but were only used by the deleted functions. This keeps the module minimal and eliminates any false sense of safety from lingering but unreachable symbols.

## Known Issues

None.

## Files Created/Modified

- `src/mermaids/pipeline/edit.py` — deleted `_CATEGORY_TO_REGION`, `generate_base_mermaid()`, `generate_dressup_variants()`, `composite_all_combinations()`; updated module docstring; removed orphaned imports
- `tests/test_masks.py` — updated stale section comment to remove `DRESSUP_VARIANTS` reference
- `.gsd/milestones/M003/slices/S03/S03-PLAN.md` — added `## Observability / Diagnostics` section per pre-flight requirement
