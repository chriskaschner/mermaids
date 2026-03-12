---
phase: 07-github-pages-deployment
verified: 2026-03-11T00:00:00Z
status: gaps_found
score: 2/3 success criteria verified
re_verification: false
gaps:
  - truth: "Opening the GitHub Pages URL on iPad Safari loads the app and both activities work correctly"
    status: failed
    reason: "Real iPad Safari UAT performed during plan 07-02 execution revealed two functional failures: dress-up part swap shows full mermaid list instead of swapping the selected part; color swatch recolors most of the mermaid instead of only the selected part. Root cause not yet diagnosed."
    artifacts:
      - path: "frontend/js/dressup.js"
        issue: "Dress-up part swap and color recolor behave incorrectly on live static site; likely JS event handler or asset path issue specific to GitHub Pages hosting vs local uvicorn"
    missing:
      - "Diagnose root cause: open DevTools on iPad Safari at https://mermaids.chriskaschner.com and capture console errors"
      - "Fix dress-up part swap so tapping a variant option replaces the displayed mermaid part (not navigates to mermaid list)"
      - "Fix color recolor so tapping a swatch affects only the selected part (not the full mermaid)"
      - "Push fix to main, confirm CI test job passes, re-verify on real iPad Safari"
  - truth: "HTTPS is enforced (http:// redirects to https://)"
    status: failed
    reason: "curl -sI http://mermaids.chriskaschner.com/ returns HTTP/1.1 200 OK with no redirect. GitHub Pages 'Enforce HTTPS' checkbox is either not enabled or not yet active for this custom domain. Plan 07-02 user_setup listed enabling this as a step."
    artifacts: []
    missing:
      - "Enable 'Enforce HTTPS' in GitHub repo Settings -> Pages if not already checked"
      - "Confirm http://mermaids.chriskaschner.com redirects to https:// (301 or 302)"
human_verification:
  - test: "Re-verify dress-up on real iPad Safari after fix is deployed"
    expected: "Tapping a tail/hair/accessory option in the selection panel swaps the displayed mermaid part on screen. Tapping a color swatch recolors only the selected part."
    why_human: "Playwright WebKit on Linux does not replicate real iPad Safari touch event dispatch and rendering faithfully. DPLY-03 requires real-device verification."
  - test: "Verify coloring activity on real iPad Safari"
    expected: "Tapping a color swatch then tapping a white region flood-fills that region. Undo reverts the last fill."
    why_human: "Coloring activity was not explicitly tested during the 07-02 verification pass. Status is unknown."
---

# Phase 7: GitHub Pages Deployment Verification Report

**Phase Goal:** The app is live on GitHub Pages and usable on her iPad without running a local server
**Verified:** 2026-03-11
**Status:** gaps_found
**Re-verification:** No -- initial verification

## Goal Achievement

### Success Criteria (from ROADMAP.md)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The frontend/ directory is deployed to GitHub Pages as a static site | VERIFIED | `curl https://mermaids.chriskaschner.com/` returns HTTP 200 from GitHub.com server; DNS CNAME `mermaids.chriskaschner.com -> chriskaschner.github.io.` confirmed |
| 2 | All asset references use relative paths (no broken loads from absolute /assets/ paths) | VERIFIED | grep scan of `frontend/js/*.js` and `frontend/index.html` found zero absolute `/assets`, `/js`, `/css` path prefixes; index.html uses `src="js/app.js?v=14"` |
| 3 | Opening the GitHub Pages URL on iPad Safari loads the app and both activities work correctly | FAILED | Real iPad Safari UAT (07-02 Task 3) confirmed: dress-up part swap broken (shows mermaid list instead of swapping part); color swatch recolors wrong scope |

**Score:** 2/3 success criteria verified

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|---------------|-------------|--------|----------|
| DPLY-01 | 07-01, 07-02 | frontend/ deploys to GitHub Pages as static site | SATISFIED | Site live at https://mermaids.chriskaschner.com (HTTP 200); `frontend/CNAME` contains `mermaids.chriskaschner.com`; DNS CNAME resolves to `chriskaschner.github.io.` |
| DPLY-02 | 07-01, 07-02 | All asset paths are relative (no absolute /assets/ paths) | SATISFIED | No absolute paths found in frontend/. Note: REQUIREMENTS.md describes DPLY-02 as "relative paths" requirement; this is fully met. The CI test gate (originally in plan scope) is implemented as the mechanism that verifies DPLY-01. |
| DPLY-03 | 07-01, 07-02 | App is accessible on iPad Safari via GitHub Pages URL | NOT SATISFIED | iPad Safari UAT failed: two functional failures confirmed on live site. REQUIREMENTS.md explicitly marks this `[ ]` with GAP note. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/conftest.py` | BASE_URL env var guard in live_server fixture | VERIFIED | `import os` present; `os.environ.get("BASE_URL")` guard at fixture top; yields BASE_URL directly if set; uvicorn path unchanged |
| `.github/workflows/deploy.yml` | CI test job gating deploy | VERIFIED | `test` job present with `astral-sh/setup-uv@v4`, `python -m http.server 8080`, `BASE_URL: http://127.0.0.1:8080` env; `deploy` job has `needs: [test]` |
| `frontend/CNAME` | Custom domain declaration | VERIFIED | Contains exactly `mermaids.chriskaschner.com` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `.github/workflows/deploy.yml test job` | `tests/conftest.py live_server fixture` | `BASE_URL: http://127.0.0.1:8080` env var in CI step | WIRED | deploy.yml line 43: `BASE_URL: http://127.0.0.1:8080` under `env:` for E2E test step; conftest.py line 37: `base_url = os.environ.get("BASE_URL")` |
| `deploy job` | `test job` | `needs: [test]` | WIRED | deploy.yml line 51: `needs: [test]` present |
| `DNS CNAME record` | `chriskaschner.github.io` | `mermaids.chriskaschner.com CNAME` | WIRED | `dig mermaids.chriskaschner.com CNAME +short` returns `chriskaschner.github.io.` |
| `GitHub Pages custom domain` | `mermaids.chriskaschner.com` | Settings UI + `frontend/CNAME` | WIRED | Site resolves and returns HTTP 200 from GitHub.com at the custom domain |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | - | - | - | - |

No TODO/FIXME/placeholder comments or empty implementations found in phase-modified files (`tests/conftest.py`, `.github/workflows/deploy.yml`, `frontend/CNAME`).

### Commit Verification

All commits documented in summaries verified present in git log:

| Commit | Description |
|--------|-------------|
| `a234d2e` | feat(07-01): update live_server fixture for BASE_URL env var |
| `ce2fbb3` | feat(07-01): add CI test job to deploy.yml gating deploy on E2E pass |
| `a01682e` | chore(07-02): add frontend/CNAME for custom domain declaration |
| `d220043` | chore(07-02): configure DNS and GitHub Pages custom domain |
| `28edf68` | docs(07-02): record iPad Safari verification failure -- DPLY-03 not met |

### Deferred Items (Pre-existing, Out of Scope)

Per `deferred-items.md`:
- `test_tap_region_triggers_sparkle[webkit]` and `test_sparkle_cleanup[webkit]` fail against both uvicorn and `python -m http.server`. Pre-existing, not caused by phase 7 changes. 2 of 62 E2E tests fail; 60 pass.

### Human Verification Required

#### 1. Dress-Up Activity Re-verification on Real iPad Safari

**Test:** After fix is deployed, open https://mermaids.chriskaschner.com on a real iPad running Safari. Tap the Dress-Up activity. Tap a tail, hair, or accessory option in the selection panel.
**Expected:** The displayed mermaid part updates to the selected variant. Tapping a color swatch recolors only the selected part (not the full mermaid).
**Why human:** Real iPad Safari touch event dispatch and rendering are not faithfully replicated by Playwright WebKit on Linux. DPLY-03 requires real-device confirmation.

#### 2. Coloring Activity Verification on Real iPad Safari

**Test:** Open https://mermaids.chriskaschner.com on a real iPad running Safari. Tap the Coloring activity. Select a color swatch, then tap a white region on the coloring page. Tap Undo.
**Expected:** The tapped region fills with the selected color. Undo reverts the last fill. Performance is acceptable (no crash or degradation).
**Why human:** Coloring activity was not tested during the 07-02 verification pass. Status is unknown.

### Gaps Summary

**Gap 1 (Blocking -- DPLY-03):** iPad Safari dress-up interaction is broken on the live site. Two failures confirmed on real device: part swap opens the full mermaid list navigation instead of replacing the displayed part, and color swatch recolors a broad area rather than the selected part. The root cause has not been diagnosed. Candidates per 07-02-SUMMARY are: JS errors specific to static hosting, asset path resolution differences on GitHub Pages vs local dev server, or event handler binding not surviving the build/deploy pipeline. DevTools console inspection on the live site is the first diagnostic step required.

**Gap 2 (Secondary):** HTTP does not redirect to HTTPS. `curl -sI http://mermaids.chriskaschner.com/` returns `HTTP/1.1 200 OK` with no Location header. The 07-02 user_setup included enabling "Enforce HTTPS" in GitHub Pages Settings. This checkbox may not have been activated, or it may require additional DNS propagation time. This is a security/UX gap but does not prevent the app from being usable.

**Root cause grouping:** Gap 1 likely shares a common root cause with the dress-up behavior seen in CI (the 2 pre-existing webkit failures involving `[data-region="tail"]` locator not found). Both may point to a structural issue with how the static frontend renders dress-up component state. A single focused investigation of the dress-up JS on the live site may close Gap 1 entirely.

---

_Verified: 2026-03-11_
_Verifier: Claude (gsd-verifier)_
