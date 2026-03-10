---
phase: 5
slug: flood-fill-coloring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 5 — Validation Strategy

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

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 0 | CLRV-01 | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasFloodFill::test_tap_fills_region -x` | No -- Wave 0 | pending |
| 05-01-02 | 01 | 0 | CLRV-02 | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasOverlay::test_svg_overlay_present -x` | No -- Wave 0 | pending |
| 05-01-03 | 01 | 0 | CLRV-03 | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasFloodFill::test_fill_stops_at_lines -x` | No -- Wave 0 | pending |
| 05-01-04 | 01 | 0 | CLRV-04 | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasMemory::test_canvas_released_on_nav -x` | No -- Wave 0 | pending |
| 05-01-05 | 01 | 0 | CLRV-05 | E2E (Playwright) | `uv run pytest tests/test_coloring.py::TestCanvasUndo::test_undo_reverts_fill -x` | No -- Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_coloring.py` -- FULL REWRITE: existing tests use SVG data-region pattern; new tests must verify canvas flood fill, SVG overlay, ImageData undo, canvas cleanup
- [ ] Existing test structure (conftest.py with live_server, iPad emulation, Playwright) is reusable as-is

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Fill spread animation visual quality | CLRV-01 | Visual aesthetic judgment | Trigger fill on iPad, observe animation smoothness and appearance |

*All core behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
