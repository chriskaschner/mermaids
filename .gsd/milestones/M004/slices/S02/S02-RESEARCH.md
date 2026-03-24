# S02 Research: Icon Refresh

**Slice:** S02 — Icon Refresh
**Risk:** Low
**Calibration:** Light research — cosmetic SVG path replacement in two known files with no external dependencies.

## Requirement Coverage

**Owns:** ICON-01 — All navigation and activity icons are semantically meaningful.
- Status: active / unmapped validation
- Scope: nav bar (3 icons in `index.html`) + home screen activity buttons (2 icons in `app.js` `renderHome()`)
- Validation target: icons are present, visually distinct, and semantically match their activity

---

## Summary

S02 is a pure SVG path replacement in exactly two files. No logic changes, no new routes, no JS behavior changes. The work is:

1. Replace the dress-up star path in `frontend/index.html` (nav bar) with a mermaid tail SVG
2. Replace the dress-up star-in-circle path in `frontend/js/app.js` (`renderHome()`) with a mermaid tail SVG
3. Add an E2E test asserting icon semantics (distinct `aria-label` attributes, SVG presence)

The coloring pencil and home house icons are already semantically appropriate. Only the dress-up icon is broken.

---

## Implementation Landscape

### File 1: `frontend/index.html` — Nav bar icons (lines 14–31)

Three `<a class="nav-icon">` links with inline SVG children:

| Nav item | Current SVG | Semantic? | Action needed |
|---|---|---|---|
| Home (`data-view="home"`) | House shape (`M5 14L16 4L27 14V27…`) | ✓ Yes | No change |
| Dress-up (`data-view="dressup"`) | **5-pointed star** (`M16 2L18 10L26 10…`) | ✗ No | Replace with mermaid tail |
| Coloring (`data-view="coloring"`) | Paintbrush/pencil (`M6 26L8 18L22 4…`) | ✓ Yes | No change |

The SVG container is `width="32" height="32" viewBox="0 0 32 32"`.

The dress-up star path to replace:
```html
<path d="M16 2L18 10L26 10L20 15L22 23L16 18L10 23L12 15L6 10L14 10Z" stroke="#c47ed0" stroke-width="2" fill="#f0d4f5"/>
```

### File 2: `frontend/js/app.js` — `renderHome()` (lines 28–51)

Two `<a class="activity-btn">` links with 80×80 inline SVGs:

| Button | Current SVG | Semantic? | Action needed |
|---|---|---|---|
| Dress-up (`.activity-btn--dressup`) | Star in a circle + tail curve | ✗ Partial | Replace star with mermaid tail |
| Coloring (`.activity-btn--coloring`) | Pencil + highlight in a circle | ✓ Yes | No change |

The dress-up home button has:
- A circle background (keep — matches the coloring button's circle background)
- A star path: `M40 12L44 28L56 28L46 38L50 54L40 44L30 54L34 38L24 28L36 28Z` (replace)
- A tail curve: `M28 58Q34 52 40 56Q46 52 52 58` (this _is_ a tail/fin shape — can be promoted/enlarged as the primary icon)

### File 3: `tests/test_e2e.py` — Add icon assertion test

Current tests covering icons:
- `test_tap_targets_minimum_size` — asserts `.nav-icon` elements ≥ 60×60px (line 117–126)
- `test_nav_visible_on_all_views` — asserts `#nav-bar` visible (line 67–75)
- `test_nav_switching` — functional test clicking coloring nav icon (line 76–88)

No test currently asserts icon semantic content (aria-label correctness, SVG presence, visual distinctness).

A new test class `TestIconSemantics` should assert:
- Each `.nav-icon` has a non-empty `aria-label` attribute
- Nav icon `aria-labels` are all distinct (home ≠ dress-up ≠ coloring)
- Each `.nav-icon` contains an `<svg>` child element
- Each `.activity-btn` contains an `<svg>` child element
- Activity button aria-labels match expected values ("Dress Up", "Coloring")

This is a DOM assertion test — no visual rendering required. Can use `page.evaluate()` or Playwright `locator.get_attribute()`.

---

## Mermaid Tail Icon Design

The tail is the obvious semantic icon for dress-up. A simple 32×32 bifurcated tail:

**Nav bar (32×32 viewBox):** Two lobes splitting from a central stem — recognizable as a mermaid tail fin. Example paths (SVG sketch):
```
<!-- Tail stem: narrow vertical -->
<path d="M16 8 L16 20" stroke="#c47ed0" stroke-width="2.5" stroke-linecap="round"/>
<!-- Left fin lobe -->
<path d="M16 20 Q8 24 6 28" stroke="#c47ed0" stroke-width="2.5" stroke-linecap="round" fill="none"/>
<!-- Right fin lobe -->
<path d="M16 20 Q24 24 26 28" stroke="#c47ed0" stroke-width="2.5" stroke-linecap="round" fill="none"/>
<!-- Fill between lobes -->
<path d="M6 28 Q16 22 26 28" stroke="#c47ed0" stroke-width="2" fill="#f0d4f5"/>
```

**Home screen (80×80 viewBox):** Same tail motif scaled up, centered in circle background.

The executor should use simple geometry — a Y-fork or bifurcated fan shape. The existing `M28 58Q34 52 40 56Q46 52 52 58` tail-curve in the home button is a good starting point for the 80×80 version (single fin curve), but a bifurcated tail is more iconic.

---

## Constraints & Gotchas

1. **CSS classes drive styling, not icon shape** — `.activity-btn--dressup` background (`#f5e6fa`) and box-shadow stay unchanged. Only the inline SVG `<path>` data changes.

2. **No `<img>` tags for icons** — all icons are inline SVG in HTML/JS strings. No external files to add.

3. **`app.js` version cache-busting** — the script tag uses `?v=14`. Incrementing this is not required for the icon change itself (no new behavior), but the milestone may bump it for other changes.

4. **`renderHome()` is a template literal** — the SVG is inside a JS template string. Paths with backtick characters would break the template; standard SVG path data (M, L, Q, C, Z, digits, spaces) is safe.

5. **Test count baseline: 111 tests** (from `--collect-only`). Milestone target is 104+. Adding 2–4 new icon semantic tests keeps the count well above target.

6. **Existing tap target test already covers icon sizing** — new icon SVG must render within the 60×60 `.nav-icon` container. The test at line 117–126 of `test_e2e.py` will catch any regression.

7. **No CSS changes needed** — `.nav-icon` and `.activity-btn` CSS is already correctly styled. The icon change is purely SVG path data.

---

## Recommendation

**Approach:** Single-pass SVG path replacement.

1. Design a 32×32 bifurcated mermaid tail SVG path (2–3 paths max)
2. Replace the star path in `index.html` nav bar
3. Replace the star path + tail-curve in `renderHome()` in `app.js` with a single unified tail icon (matching the 80×80 circle container)
4. Add `class TestIconSemantics` to `tests/test_e2e.py` with 3–4 DOM assertion tests
5. Update `REQUIREMENTS.md` ICON-01 validation field to "validated" once tests pass

**Do not:**
- Change CSS classes or styling
- Touch the coloring pencil or home house icons (already correct)
- Modify any JS routing, event handlers, or data structures
- Add external SVG asset files (inline is the existing pattern)

---

## Verification Commands

```bash
# Run full test suite — must stay at 104+ tests passing
cd /path/to/project && .venv/bin/python -m pytest tests/ -x -q

# Run only E2E tests (requires live server fixture in conftest.py)
.venv/bin/python -m pytest tests/test_e2e.py -x -q

# Quick DOM check (after dev server running):
# Open browser devtools console on localhost and verify:
# document.querySelectorAll('.nav-icon').forEach(el => console.log(el.getAttribute('aria-label'), el.querySelector('svg')))
```
