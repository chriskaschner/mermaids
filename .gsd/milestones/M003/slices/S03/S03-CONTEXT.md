---
id: S03
milestone: M003
status: ready
---

# S03: Cleanup & Stability — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Fix known bugs, remove dead code from the pipeline pivot, and close M003 with a clean codebase and all tests green.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

S01 reworks the dress-up art (grouping, clipping, hair-only recoloring) and S02 fixes coloring page outline gaps. Both leave behind a codebase with known bugs found during UAT, dead code from the architecture pivot (multi-layer part-swapping → flat gallery), and leftover generated assets. S03 is the final slice that cleans this up, fixes outstanding bugs, adds tests for the fixes, and closes out M003 with confidence that the app works correctly end-to-end.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- **Fix fetch 404 handling:** `renderDressUp()` in `app.js` does not check `resp.ok` after `fetch("assets/svg/mermaid.svg")`. A 404 injects the HTML error page as SVG content instead of showing the `<div class="error">` fallback. Fix all `fetch()` calls in `app.js` to check `resp.ok` and surface proper error UI. (Found in S01 UAT.)
- **Fix WebKit sparkle failures (DEBT-02):** 2 known WebKit sparkle test failures. Investigate and fix or mark as known-skip with a clear reason.
- **Remove dead pipeline code:** `composite_all_combinations()` in `edit.py` is no longer used since the pivot from multi-layer compositing to flat character gallery. Remove it and any supporting functions/imports that exist solely for the old approach.
- **Remove unused variant infrastructure:** `DRESSUP_VARIANTS` (if still referenced), old part-SVG generation code, and any imports that reference the abandoned multi-layer architecture.
- **Clean up leftover generated assets:** Remove old generated files from prior pipeline runs that are no longer used — e.g., combo PNGs/SVGs in `assets/generated/png/dressup/composites/`, `assets/generated/png/dressup/parts/`, `assets/generated/svg/dressup/composites/`, and `assets/generated/svg/dressup/assembled/` if they contain stale outputs.
- **Add tests for fixed bugs:** Write tests that verify the fetch 404 handling shows the error div and that sparkle behavior works in the target browser engine.
- **All tests green:** Full test suite (currently 102 tests) must pass with no failures, no skips (unless explicitly justified for WebKit engine limitations).

### Out of Scope

- New features or UX changes.
- iPad-specific memory/stability testing (existing `releaseCanvas()` and router cleanup are trusted).
- Manual iPad UAT — the done signal is green automated tests + clean code.
- Performance optimization.
- Adding new coloring pages or character designs.
- Wiring per-part recoloring for tail/eyes/accessories (groups exist from S01 but only hair recoloring is active).

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- **Depends on S01 and S02 being complete.** S01 restructures the mermaid SVGs with groups and clipPaths; S02 post-processes coloring page outlines. S03 must not conflict with or undo those changes.
- **No functional regressions:** The app must work identically to post-S02 state. Cleanup and bug fixes only — no behavior changes beyond fixing the specific bugs listed.
- **Dead code removal must be safe:** Only remove code that is confirmed unreachable. The pipeline modules (`edit.py`, `assemble.py`) are used by scripts and tests — verify no test depends on the removed code before deleting.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `frontend/js/app.js` — fetch calls that need `resp.ok` checks
- `frontend/js/sparkle.js` — WebKit sparkle behavior (DEBT-02)
- `src/mermaids/pipeline/edit.py` — contains `composite_all_combinations()` and old variant infrastructure to remove
- `src/mermaids/pipeline/assemble.py` — may have dead code referencing old combo/layer structure
- `assets/generated/` — leftover files from prior pipeline approaches
- `tests/` — all test files, to verify nothing depends on removed code

### Produces

- Updated `frontend/js/app.js` — fetch calls check `resp.ok`; error UI works on 404
- Updated `frontend/js/sparkle.js` — WebKit sparkle fix or documented skip
- Cleaned `src/mermaids/pipeline/edit.py` — dead composite code removed
- Cleaned `src/mermaids/pipeline/assemble.py` — dead combo/layer code removed
- Cleaned `assets/generated/` — stale intermediate files removed
- New tests covering fetch error handling and sparkle behavior
- Full green test suite (102+ tests)

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- **DEBT-02 WebKit sparkle resolution** — Are the WebKit failures a timing issue (sparkle DOM elements not found within the test wait window), a rendering difference (WebKit doesn't fire the same animation events), or an actual bug? — *Current thinking: investigate first. If it's a timing issue, increase wait time. If it's a WebKit rendering limitation, skip with `@pytest.mark.skip(reason="WebKit sparkle timing")` and document.*
- **Scope of dead code in edit.py** — `DRESSUP_VARIANTS` is referenced in `edit.py` but may also be imported by tests. Need to trace all references before removing. — *Current thinking: `rg DRESSUP_VARIANTS` to find all usages, remove if only in dead paths, update tests if they reference it.*
- **Generated asset cleanup boundaries** — The `assets/generated/png/dressup/base/` and `assets/generated/png/dressup/parts/` directories contain files from the edit API approach. Are they safe to remove, or does any script still reference them? — *Current thinking: check `rg` for path references, remove if unreferenced. Keep the 9 `mermaid-{1..9}.png` files in the parent dressup directory since those are the active character sources.*
