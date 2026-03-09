---
phase: 2
slug: dress-up
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ with pytest-playwright 0.7.2 |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest tests/ -x` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | DRSS-01 | e2e | `uv run pytest tests/test_dressup.py::TestDressUpView::test_mermaid_visible -x` | -- W0 | pending |
| 02-01-02 | 01 | 0 | DRSS-02 | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_tail_swap -x` | -- W0 | pending |
| 02-01-03 | 01 | 0 | DRSS-03 | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_hair_swap -x` | -- W0 | pending |
| 02-01-04 | 01 | 0 | DRSS-04 | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping::test_accessory_swap -x` | -- W0 | pending |
| 02-01-05 | 01 | 0 | DRSS-05 | e2e | `uv run pytest tests/test_dressup.py::TestColorRecolor::test_color_swatch_changes_fill -x` | -- W0 | pending |
| 02-01-06 | 01 | 0 | DRSS-06 | e2e | `uv run pytest tests/test_dressup.py::TestUndo::test_undo_reverts_swap -x` | -- W0 | pending |
| 02-01-07 | 01 | 0 | DRSS-07 | e2e | `uv run pytest tests/test_dressup.py::TestCompletion::test_celebration_sparkle -x` | -- W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_dressup.py` -- Playwright E2E tests for all DRSS requirements
- [ ] Existing `tests/test_e2e.py` -- may need updates if `renderDressUp()` changes significantly

*Existing test infrastructure (pytest, playwright, conftest) covers framework setup.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual quality of SVG variants | DRSS-02/03/04 | Aesthetic judgment | Visually inspect each tail/hair/accessory variant for artistic quality |
| Color palette aesthetics | DRSS-05 | Aesthetic judgment | Verify color swatches look child-friendly and visually appealing |
| Celebration animation feel | DRSS-07 | Subjective quality | Verify sparkle animation feels satisfying and celebratory |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
