---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 1 -- Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ with pytest-playwright 0.6+ |
| **Config file** | none -- Wave 0 installs |
| **Quick run command** | `uv run pytest tests/ -x --timeout=30` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x --timeout=30`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FOUN-01 | e2e | `uv run pytest tests/test_e2e.py::test_tap_targets_minimum_size -x` | -- W0 | pending |
| 01-01-02 | 01 | 1 | FOUN-02 | e2e | `uv run pytest tests/test_e2e.py::test_mermaid_svg_visible -x` | -- W0 | pending |
| 01-01-03 | 01 | 1 | FOUN-03 | manual-only | Visual inspection of rendered SVG on iPad | N/A | pending |
| 01-01-04 | 01 | 1 | FOUN-04 | e2e | `uv run pytest tests/test_e2e.py::test_tap_triggers_feedback -x` | -- W0 | pending |
| 01-01-05 | 01 | 1 | NAVG-01 | e2e | `uv run pytest tests/test_e2e.py::test_navigation_between_views -x` | -- W0 | pending |
| 01-01-06 | 01 | 1 | NAVG-02 | e2e | `uv run pytest tests/test_e2e.py::test_navigation_between_views -x` | -- W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` -- project setup with dependencies
- [ ] `tests/conftest.py` -- shared fixtures (FastAPI test server, Playwright browser context with iPad settings)
- [ ] `tests/test_app.py` -- FastAPI static file serving tests
- [ ] `tests/test_pipeline.py` -- vtracer SVG tracing pipeline tests
- [ ] `tests/test_e2e.py` -- Playwright iPad emulation E2E tests
- [ ] Framework install: `uv add --dev pytest playwright pytest-playwright httpx && uv run playwright install webkit`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Consistent watercolor art style | FOUN-03 | Visual quality is subjective; requires human judgment on art style consistency | 1. Open app on iPad Safari 2. Verify mermaid SVG has watercolor-style appearance 3. Check texture consistency across all SVG regions |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
