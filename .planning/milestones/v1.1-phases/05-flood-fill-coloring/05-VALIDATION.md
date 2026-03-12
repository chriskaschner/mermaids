---
phase: 5
slug: flood-fill-coloring
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-09
---

# Phase 5 -- Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ with playwright (sync_api) |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest tests/test_coloring.py -x` |
| **Full suite command** | `uv run pytest tests/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_coloring.py -x`
- **After every plan wave:** Run `uv run pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

Note: This phase has no dedicated Wave 0 plan. Plan 01 (Wave 1) creates the algorithm modules with their own unit tests. Plan 02 (Wave 2) rewrites the E2E tests as Task 1 (RED), then implements app.js integration as Task 2 (GREEN).

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | CLRV-01, CLRV-03 | Unit (Playwright) | `uv run pytest tests/test_floodfill_unit.py -x` | No -- created by Plan 01 Task 1 | pending |
| 05-01-02 | 01 | 1 | CLRV-05 | Unit (Playwright) | `uv run pytest tests/test_floodfill_unit.py -x` | No -- created by Plan 01 Task 1 | pending |
| 05-02-01 | 02 | 2 | CLRV-01..05 | E2E (Playwright) | `python -c "import ast; ast.parse(open('tests/test_coloring.py').read())"` | Yes -- rewritten (RED state) | pending |
| 05-02-02 | 02 | 2 | CLRV-01..05 | E2E (Playwright) | `uv run pytest tests/test_coloring.py tests/test_floodfill_unit.py -x` | Yes -- tests go GREEN | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

This phase has no Wave 0 plan. The E2E test rewrite happens as Plan 02 Task 1 (first task of Wave 2), establishing test expectations before the implementation in Plan 02 Task 2. Plan 01's unit tests (`test_floodfill_unit.py`) are created alongside the algorithm modules in Wave 1.

- [ ] `tests/test_floodfill_unit.py` -- created by Plan 01 Task 1 (TDD: tests + algorithm together)
- [ ] `tests/test_coloring.py` -- FULL REWRITE in Plan 02 Task 1 (RED), validated GREEN in Plan 02 Task 2
- [ ] Existing test structure (conftest.py with live_server, iPad emulation, Playwright) is reusable as-is

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Fill spread animation visual quality | CLRV-01 | Visual aesthetic judgment | Trigger fill on iPad, observe animation smoothness and appearance |

*All core behaviors have automated verification.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave structure accurately reflected in verification map
- [ ] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
