---
phase: 4
slug: art-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >= 8 |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest tests/test_pipeline.py -x` |
| **Full suite command** | `uv run pytest tests/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_pipeline.py tests/test_generate.py tests/test_masks.py tests/test_assemble.py -x`
- **After every plan wave:** Run `uv run pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | ARTP-01 | unit (mocked API) | `uv run pytest tests/test_generate.py::test_coloring_generation -x` | W0 | pending |
| 04-01-02 | 01 | 0 | ARTP-01 | unit | `uv run pytest tests/test_generate.py::test_idempotent_skip -x` | W0 | pending |
| 04-01-03 | 01 | 0 | ARTP-01 | unit (mocked) | `uv run pytest tests/test_generate.py::test_retry_backoff -x` | W0 | pending |
| 04-02-01 | 02 | 1 | ARTP-02 | unit | `uv run pytest tests/test_pipeline.py::test_trace_produces_valid_svg -x` | Exists | pending |
| 04-02-02 | 02 | 1 | ARTP-02 | unit | `uv run pytest tests/test_pipeline.py::test_simplify_produces_fewer_paths -x` | Exists | pending |
| 04-03-01 | 03 | 0 | ARTP-03 | unit | `uv run pytest tests/test_masks.py::test_mask_transparency -x` | W0 | pending |
| 04-03-02 | 03 | 1 | ARTP-03 | unit (mocked API) | `uv run pytest tests/test_generate.py::test_dressup_edit -x` | W0 | pending |
| 04-04-01 | 04 | 2 | ARTP-04 | unit | `uv run pytest tests/test_assemble.py::test_defs_use_structure -x` | W0 | pending |
| 04-04-02 | 04 | 2 | ARTP-04 | unit | `uv run pytest tests/test_assemble.py::test_variant_ids -x` | W0 | pending |
| 04-04-03 | 04 | 2 | ARTP-04 | smoke | `uv run pytest tests/test_assemble.py::test_output_paths -x` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_generate.py` -- stubs for ARTP-01, ARTP-03 (mocked OpenAI API calls)
- [ ] `tests/test_masks.py` -- stubs for ARTP-03 (mask creation, RGBA format verification)
- [ ] `tests/test_assemble.py` -- stubs for ARTP-04 (SVG assembly, defs+use structure)
- [ ] OpenAI SDK mock fixtures in conftest.py or test_generate.py

*Existing infrastructure covers ARTP-02 via tests/test_pipeline.py.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual quality of generated kawaii mermaid PNGs | ARTP-01 | Subjective aesthetic judgment | Run generate script, visually inspect output PNGs for kawaii style |
| SVG renders correctly in browser | ARTP-04 | Requires browser rendering | Open assembled SVGs in browser, verify clean line art renders |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
