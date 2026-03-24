# KNOWLEDGE.md — Project-Specific Gotchas and Patterns

## Dress-Up Recoloring: CSS hue-rotate, NOT fill manipulation

**Context:** M003 / S01 / T03

The dress-up recoloring uses `svg.style.filter = 'hue-rotate(Xdeg)'` applied to the whole `<svg>` element — it does NOT modify individual `path[fill]` attributes. The old fill-manipulation heuristic (exclude dark/skin/white fills) completely broke on darker-skinned characters where ALL fills matched exclusion criteria.

**Gotcha:** Tests that check recoloring by reading `path.getAttribute('fill')` will always pass vacuously (fills never change with hue-rotate) or fail if they assert a specific color was set. Assert `svg.style.filter.includes('hue-rotate')` instead.

**Why hue-rotate:** Proportionally shifts every color in the SVG, preserving the character's relative color relationships. Works universally across all 9 diverse mermaid characters.

---

## Architecture Pivot: Multi-Layer Parts → Flat Character Gallery

**Context:** M003 / S01

The original plan (T01/T02/T03 as written) targeted a multi-layer part-swapping architecture: 1 base body + 12 isolated part variants in 5 stacked `<use>` layers. This was fully implemented (prompts.py, assemble.py, dressup.js, tests) but then replaced by a flat 9-character gallery approach.

**Why the pivot:** The gpt-image-1 edit API outputs full characters, not isolated parts. Clipping/compositing produced visible seams. Character gallery (9 diverse full mermaids, swap whole SVG) solved the art quality problem cleanly.

**Evidence:** WORKLOG.md, commit `39336c0`, `.planning/phases/08-dress-up-art-rework/.continue-here.md`.

**Future agents:** When resuming this project, read WORKLOG.md and `.planning/STATE.md` first — they accurately reflect the pivoted architecture. GSD milestone/slice plans may describe the original approach.

---

## vtracer Full-Color Tracing: Use simplify=False for AI Art

**Context:** M003 art pipeline

vtracer's binary mode (default) produces very few paths (<10) on AI-generated character images. Full-color mode with `simplify=False` is required to get >50 paths needed for the test assertion `path_count > 50` (and produces much better visual fidelity).

## SVG Path Y-Range Extraction: Must Parse C (Cubic Bezier) Commands

**Context:** M003 / S01 / T04

When extracting bounding-box y-coordinates from vtracer-generated SVG path data, parsing only M (moveto) and L (lineto) commands returns nearly zero extent. These paths consist almost entirely of C (cubic bezier) commands. A path with 1 M command and 103 C commands looks "zero height" if you only regex `[ML]\s*x\s+y`.

**Fix:** Also extract y from C commands: `C x1 y1 x2 y2 x y` — extract all three y values (y1, y2, y endpoint) from each C segment. Pattern: `re.findall(r'C\s*((?:[-\d.]+\s+[-\d.]+\s+){0,3})', d)` then parse pairs from each group.

**Gotcha:** If your y_max analysis shows a path has y_max ≈ translate_y (transform offset only), you're only seeing the M command y=0, not the actual path extent.

## SVG clipPath Rect Must Be Oversized to Handle Negative Local Coordinates

**Context:** M003 / S01 / T04

SVG path data uses local coordinates (relative to the transform origin), and transform="translate(x, y)" offsets them to absolute canvas position. Paths often have control points with negative local y values (e.g., y=-2 with ty=60 → absolute y=58). If your clipPath rect starts at y=0, you'd cut off the top of paths that have small negative local coordinates.

**Fix:** Use an oversized rect: `<rect x="-512" y="-512" width="2048" height="clipY+512"/>` where clipY is your desired absolute clip boundary. The ±512 buffer handles all observed path data extents in this project's mermaid SVGs.

## Gallery grid item overlap with aspect-ratio in Playwright tests

**Context:** Adding items to a 2-column CSS grid where items use `aspect-ratio: 3/4`. When the grid container has `height: 100%` and `align-content: center`, expanding from 4 to 9 items causes CSS grid to calculate item heights based on the container height rather than the aspect-ratio — resulting in row heights that cause visual/hit-test overlap between adjacent rows in Playwright's viewport (1280×800).

**Fix:** Add `max-height` to `.gallery-thumb` (e.g. `max-height: 260px`) to bound the aspect-ratio expansion. Also add `overflow-y: auto; align-content: start` to the gallery container, and `pointer-events: none` to gallery thumb `<img>` elements to prevent hit-test intercepts.

**Signal:** Playwright error "element intercepts pointer events" pointing to a DIFFERENT grid row than the one being clicked.

---

## The Dress-Up Initial SVG Is mermaid.svg, Not dressup/mermaid-1.svg

**Context:** M004 / S01 / T01

The dress-up screen loads `assets/svg/mermaid.svg` (not `dressup/mermaid-1.svg`) as its initial display SVG. Character swapping (clicking a character button) then replaces it with `assets/svg/dressup/mermaid-N.svg`. These are two distinct files even though mermaid-1 and mermaid.svg share content.

**Gotcha:** If you add `<g id="hair-group">` to all 9 `dressup/mermaid-N.svg` files but not to `mermaid.svg`, recoloring on the initial (pre-swap) state silently no-ops because `#hair-group` doesn't exist in the DOM.

**Fix:** Apply the same hair-group wrapper to `mermaid.svg` as well.

---



**Context:** M003 / S03 / T02

When verifying dead Python code is fully removed, `grep -rn "symbol_name" src/` will match stale `.pyc` bytecode files in `__pycache__/` directories. This produces false positives that look like the dead code still exists.

**Fix:** Always use `grep --include="*.py" -rn "symbol_name" src/ scripts/ tests/` for source-clean verification. The bytecode is regenerated on next import and does not represent live code.

**Gotcha:** CI/CD environments that cache `__pycache__` may trigger this more often than local dev.

---

## Fetch Error Guards: Always Check resp.ok Before Reading Body

**Context:** M003 / S03 / T01

Frontend `fetch()` calls that skip the `resp.ok` check silently accept HTTP error responses. When fetching SVG, this injects the server's HTML error page as SVG content, corrupting the UI with no visible error. The failure mode is silent — the app renders broken content instead of showing an error.

**Fix:** After every `fetch()`, immediately check `if (!resp.ok) throw new Error(...)` before calling `resp.text()` or `resp.json()`. Keep the throw inside the existing try/catch so the UI error handler displays it.

**Pattern:** `const resp = await fetch(url); if (!resp.ok) throw new Error(\`Failed: \${resp.status}\`); const data = await resp.text();`

---

## SVG XML Comments Must Not Contain `--` (Double Hyphen) or Non-ASCII

**Context:** M004 / S01 / T03

Chromium's SVG image renderer (used when loading SVG via `new Image()` for canvas rasterization) enforces strict XML validation. Two categories of invalid XML in SVG comments cause silent `img.onerror` with no console message pointing to the XML issue:

1. **Double hyphen `--` inside comments**: Per the XML spec, `--` is illegal inside comment content. Example: `<!-- Generated by script --placeholder -->` (the `--placeholder` part is invalid). Chromium rejects the whole SVG file.
2. **Non-ASCII characters in comments**: Unicode box-drawing characters like `──` (U+2500) inside comments also cause rejection in some Chromium versions.

**Failure signature:** `img.onerror` fires with `Event` object (stringifies to `"Event"`). The server returns 200 OK with correct MIME type. The SVG blob URL also fails when re-fetched and loaded as a blob. Only stripping comments fixes it.

**Fix:** Use only ASCII characters in SVG comments, and avoid `--` sequences anywhere inside comment text. Replace `<!-- B&W outline -- -->` with `<!-- BandW outline -->`, `<!-- -- Head -- -->` with `<!-- Head -->`, `<!-- --placeholder -->` with `<!-- -placeholder -->`.

**Diagnosis commands:**
- Inline SVG blob loads fine but same content from server URL fails → check for non-ASCII in SVG text
- `python3 -c "d=open('file.svg','rb').read(); print([hex(b) for b in d if b>127])"` to find non-ASCII bytes
- `grep -P '[\x80-\xff]' file.svg` to find non-ASCII lines
- Bisect: load via blob URL with and without comments stripped to confirm comment-only issue

---



**Context:** M003 — multi-layer → gallery pivot

The largest architectural decision in M003 was forced by the AI model's output characteristics, not by design preference. The multi-layer part-swapping plan (1 base + 12 isolated parts) was sound in theory but collapsed when gpt-image-1 proved it generates full characters, not isolated parts. Clipping/compositing of AI output produced visible seams.

**Takeaway:** When building architecture around AI-generated assets, prototype the art pipeline BEFORE committing to the frontend architecture. The model's actual output format constrains what the frontend can do. Plan for fallback architectures when AI output doesn't match expectations.

---

## Hair Paths in Dress-Up SVGs May Not Be Consecutive

**Context:** M004 / S01 / T01

The 9 dress-up mermaid SVGs each have exactly 2 `<path>` elements with `clip-path="url(#hair-clip)"`. When wrapping these in `<g id="hair-group">`, you might assume they're adjacent lines in the SVG source. They're not always — mermaid-2.svg and mermaid-8.svg have a non-hair body path sandwiched between the two hair paths.

**Gotcha:** If you wrap a range of lines between the first and last hair path, you'll capture non-hair geometry inside the group. Hue-rotate would then recolor that body path too.

**Fix:** Identify the exact line indices of the 2 `clip-path="url(#hair-clip)"` paths and wrap only those. If non-hair paths exist between them, extract the hair paths into a clean group. A two-pass approach works: (1) insert wrapper, (2) detect and move any non-hair paths outside the group.

---

## Stub Detection for Idempotent SVG Replacement

**Context:** M004 / S03 / T01

When generating placeholder SVGs to replace empty stubs, use file size as the detection heuristic — stubs are ~170 bytes, real art is 4KB+. `scripts/generate_coloring_placeholders.py` uses a 500-byte threshold: files under 500 bytes are considered stubs and get replaced; files over 500 bytes are preserved. This makes the script safe to re-run without overwriting real (AI-generated or hand-crafted) art.

**Pattern:** `if os.path.getsize(path) < 500: generate_and_write(path)` — idempotent replacement that preserves real content.

**Gotcha:** If you add a `--force` flag to overwrite everything, document it clearly. The default behavior should always be safe/non-destructive.

---

## Hash-Based SPA Router: Query Params via Manual Splitting

**Context:** M004 / S01 / T03

The app uses hash-based routing (`#/home`, `#/dressup`, `#/coloring`). To pass parameters (e.g., which character to color), use `#/coloring?character=mermaid-3` and parse manually with `rawHash.split('?')` → `[route, queryString]`, then split `key=value` pairs. Don't use `URLSearchParams` with hash routes — it reads the `?search` portion of the URL, not parameters after the `#`.

**Pattern:** `const [route, qs] = location.hash.slice(1).split('?'); const params = Object.fromEntries((qs || '').split('&').filter(Boolean).map(p => p.split('=')));`

---

## Duplicate Flow Functions Over Shared Abstractions for Distinct User Paths

**Context:** M004 / S01 / T03

`renderColoringForCharacter()` duplicates much of `openColoringPage()` rather than sharing a common base. This was deliberate: gallery coloring (user picks from 9 pages) and dress-up coloring (user arrives with a specific character) have different back-button behavior, different error states, and different source SVGs. Sharing code would couple them and make either harder to change independently.

**Takeaway:** When two user flows look structurally similar but have different entry points, error handling, and navigation, keep them as separate functions. The duplication cost is small; the coupling cost of premature abstraction is large.
