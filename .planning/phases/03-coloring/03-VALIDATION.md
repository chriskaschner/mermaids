---
phase: 3
slug: coloring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ with pytest-playwright 0.6+ |
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
| 03-01-01 | 01 | 1 | COLR-01 | e2e | `uv run pytest tests/test_coloring.py::TestColoringGallery::test_gallery_shows_thumbnails -x` | -- Wave 0 | pending |
| 03-01-02 | 01 | 1 | COLR-01 | e2e | `uv run pytest tests/test_coloring.py::TestColoringGallery::test_thumbnail_opens_page -x` | -- Wave 0 | pending |
| 03-01-03 | 01 | 1 | COLR-02 | e2e | `uv run pytest tests/test_coloring.py::TestColoringFill::test_tap_region_fills_color -x` | -- Wave 0 | pending |
| 03-01-04 | 01 | 1 | COLR-03 | e2e | `uv run pytest tests/test_coloring.py::TestColoringPalette::test_swatches_visible -x` | -- Wave 0 | pending |
| 03-01-05 | 01 | 1 | COLR-03 | e2e | `uv run pytest tests/test_coloring.py::TestColoringPalette::test_swatch_changes_selection -x` | -- Wave 0 | pending |
| 03-01-06 | 01 | 1 | COLR-04 | e2e | `uv run pytest tests/test_coloring.py::TestColoringUndo::test_undo_reverts_fill -x` | -- Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_coloring.py` -- Playwright E2E test stubs for all COLR requirements
- [ ] Coloring page SVG assets (4-6 files in `frontend/assets/svg/coloring/`)
- [ ] `frontend/js/coloring.js` -- coloring module stub

*Existing `tests/test_e2e.py` covers navigation to coloring view but assertions are minimal.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SVG region touch targets >= 60pt | COLR-02 | Visual/ergonomic check | Open on mobile, verify child can tap each region without misses |
| Coloring page art quality | COLR-01 | Subjective visual | Review each SVG for clear outlines, distinct regions, mermaid theme |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
