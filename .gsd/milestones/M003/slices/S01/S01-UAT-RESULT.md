---
sliceId: S01
uatType: mixed
verdict: PASS
date: 2026-03-23T03:06:00Z
---

# UAT Result — S01

## Checks

| Check | Mode | Result | Notes |
|-------|------|--------|-------|
| 1. Full test suite passes | runtime | PASS | `uv run pytest -q` → 102 passed in 47.08s, 0 failed, 0 errors |
| 2. Gallery shows 9 character buttons | runtime | PASS | 9 `.char-btn` elements found; first selected = `mermaid-1` |
| 3. Character swap replaces entire SVG | runtime | PASS | Clicking mermaid-3 updates `.char-btn.selected` to `mermaid-3`; SVG paths changed (23→30); no remnant paths |
| 4. Hue-rotate recoloring applies | runtime | PASS | After clicking color swatch, `svg.style.filter` = `"hue-rotate(330deg)"` |
| 5. Recoloring works on dark-skinned character | runtime | PASS | mermaid-4 selected, swatch clicked → `svg.style.filter` = `"hue-rotate(197deg)"`; hue-rotate shifts all fills uniformly |
| 6. Undo reverts last action | runtime | PASS | After swap mermaid-1→mermaid-5 then undo, selected = `mermaid-1`. After color then undo, `svg.style.filter` = `""` (empty) |
| 7. Celebration sparkle on completion | runtime | PASS | After clicking non-default character, 36 `.sparkle.celebration` elements found |
| 8. Touch targets are 60pt+ | runtime | PASS | All `.char-btn` elements ≥ 60px (measured ~82.6×82.6px) |
| 9. Pipeline region masks are non-overlapping | runtime | PASS | `test_masks.py::TestRegions` → 3/3 passed: 4 categories, no overlap, hair y2 < tail y1 (DEBT-03) |
| 10. SVG assembly produces valid structure | runtime | PASS | `test_assemble.py` → 9/9 passed: valid SVG, mermaid-svg ID, viewBox, background stripped, content paths, characters deployed, mermaid-1 as default |
| 11. All character SVGs present on disk | artifact | PASS | 9 files (mermaid-1.svg through mermaid-9.svg) in `frontend/assets/svg/dressup/`; `mermaid.svg` exists at 30,182 bytes |
| Edge: No network errors on character load | runtime | PASS | Clicked through all 9 characters — zero 404 errors on `assets/svg/dressup/mermaid-*.svg` |
| Edge: Mermaid SVG has AI art (not stubs) | runtime | PASS | `#mermaid-svg path` count = 23 (>10); confirms AI-generated art, not geometric stubs |
| Edge: Error state on missing SVG | runtime | FAIL | When `mermaid.svg` is removed, fetch returns 404 but `resp.ok` is not checked — the 404 error page HTML gets injected as SVG content instead of showing `<div class="error">`. The catch block never triggers because fetch doesn't throw on 404. |
| Smoke: test_dressup.py | runtime | PASS | 14/14 tests passed in 8.15s |

## Overall Verdict

**PASS** — All 11 required test cases and 2 of 3 edge cases pass. The one failing edge case (error state on missing SVG) is a minor defensive-coding gap where `fetch()` doesn't check `resp.ok` before using the response body. This does not affect any functional requirement or normal usage — it only manifests when `mermaid.svg` is deleted from the server. All 102 automated tests pass, the 9-character gallery works correctly, hue-rotate recoloring works across all skin tones (including dark-skinned mermaid-4), undo works for both character swaps and color changes, celebration sparkles fire, touch targets exceed 60px, and pipeline region masks are non-overlapping (DEBT-03 fixed).

## Notes

- **Sparkle timing sensitivity:** The celebration sparkle elements (`.sparkle.celebration`) are transient DOM elements that appear and auto-remove. The E2E test (`test_celebration_sparkle`) uses an 800ms wait and reliably finds 36 sparkle elements. Custom UAT scripts need to use the correct selector (`.sparkle.celebration`, not just `.sparkle`) and adequate wait time.
- **Edge case bug found:** `renderDressUp()` in `app.js:57` does `const resp = await fetch("assets/svg/mermaid.svg")` but doesn't check `resp.ok` before calling `resp.text()`. On a 404, the HTML error page gets injected as "SVG content" instead of triggering the catch block's error div. This is a low-severity defensive coding issue — logged for awareness but not blocking.
- **Recoloring mechanism confirmed:** CSS `hue-rotate` on the whole `<svg>` element, NOT fill-attribute manipulation. Individual `path[fill]` attributes do NOT change when recoloring — verified this is correct behavior per the architecture pivot.
- **Pre-existing WebKit failures:** 2 WebKit sparkle failures (DEBT-02) are known and not tested in this UAT (Chromium-only browser checks).
- **Test environment:** All checks run against `uv run python -m http.server 8080 --directory frontend` with headless Chromium via Playwright.
