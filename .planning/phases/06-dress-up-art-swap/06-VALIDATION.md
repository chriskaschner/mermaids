---
phase: 6
slug: dress-up-art-swap
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 6 -- Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ with playwright 1.49+ |
| **Config file** | pyproject.toml [tool.pytest.ini_options] |
| **Quick run command** | `uv run pytest tests/test_dressup.py -x` |
| **Full suite command** | `uv run pytest tests/ -x` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_dressup.py -x`
- **After every plan wave:** Run `uv run pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 6-01-01 | 01 | 0 | DRSV-01 | e2e | `uv run pytest tests/test_dressup.py::TestPreviewThumbnails -x` | W0 | pending |
| 6-01-02 | 01 | 0 | DRSV-01 | e2e | `uv run pytest tests/test_dressup.py::TestPreviewColorSync -x` | W0 | pending |
| 6-01-03 | 01 | 0 | DRSV-01 | unit | `uv run pytest tests/test_assemble.py::TestCopyDressupParts -x` | W0 | pending |
| 6-01-04 | 01 | 0 | DRSV-01 | e2e | `uv run pytest tests/test_dressup.py::TestDressUpView -x` | Exists (update) | pending |
| 6-02-01 | 02 | 1 | DRSV-01 | e2e | `uv run pytest tests/test_dressup.py::TestDressUpView -x` | Exists | pending |
| 6-02-02 | 02 | 1 | DRSV-02 | e2e | `uv run pytest tests/test_dressup.py::TestPartSwapping -x` | Exists | pending |
| 6-02-03 | 02 | 1 | DRSV-03 | e2e | `uv run pytest tests/test_dressup.py::TestColorRecolor -x` | Exists | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_dressup.py::TestPreviewThumbnails` -- verify preview buttons contain fetched SVGs (not inline hardcoded)
- [ ] `tests/test_dressup.py::TestPreviewColorSync` -- verify preview reflects color override after recolor
- [ ] `tests/test_assemble.py::TestCopyDressupParts` -- verify copy_dressup_parts_to_frontend() deploys 9 SVGs
- [ ] Update `tests/test_dressup.py::TestDressUpView` to verify AI art present (e.g., check path count > 100 inside variant defs)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Kawaii art visually appealing to children | DRSV-01 | Aesthetic judgment | View dress-up screen, confirm art style is kawaii/cute |
| Body/face visual cohesion with AI parts | DRSV-01 | Visual evaluation | Mix parts from different variants, check visual harmony |
| iPad rendering performance with 500+ path thumbnails | DRSV-02 | Real device required | Test on iPad, verify no visible lag when scrolling options |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
