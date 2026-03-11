---
phase: 7
slug: github-pages-deployment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-11
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8 + pytest-playwright 0.6 |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py -x --browser webkit` |
| **Full suite command** | `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py tests/test_floodfill_unit.py --browser webkit` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py -x --browser webkit` (after starting `python -m http.server 8080 --directory frontend &`)
- **After every plan wave:** Run full suite command above
- **Before `/gsd:verify-work`:** Full suite must be green against static server; real iPad Safari verification required for DPLY-03
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | DPLY-01, DPLY-02 | E2E | `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py -x --browser webkit` | Yes (conftest.py needs BASE_URL update) | pending |
| 7-01-02 | 01 | 1 | DPLY-01, DPLY-03 | E2E | `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py --browser webkit` | Yes | pending |
| 7-02-01 | 02 | 2 | DPLY-03 | Manual | Real iPad Safari: open GitHub Pages URL, verify app loads and activities work | N/A — manual only | pending |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — add `BASE_URL` env var guard to `live_server` fixture (update existing, no new file)
- [ ] `.github/workflows/deploy.yml` — add 'test' job with static server + Playwright (update existing, no new file)

*Note: No new test files needed — existing test_e2e.py, test_coloring.py, test_dressup.py, test_floodfill_unit.py cover all requirements once conftest.py is updated.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| App loads on real iPad Safari via GitHub Pages URL | DPLY-03 | Playwright WebKit on Linux is not identical to iPad Safari; touch/viewport behaviors differ | 1. Open `https://mermaids.chriskaschner.com` on iPad Safari. 2. Verify app loads without errors. 3. Tap through dress-up activity. 4. Tap through coloring activity. 5. Confirm flood-fill coloring works with touch. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
