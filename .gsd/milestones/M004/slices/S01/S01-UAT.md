# S01 UAT: Dress-Up → Coloring Pipeline + Hair Path Fix

**Milestone:** M004  
**Slice:** S01  
**Preconditions:** App served locally (`python -m http.server` from `frontend/`) or deployed to mermaids.chriskaschner.com. Use iPad Safari or Chrome on desktop.

---

## Test Case 1: Hair Color Change Only Affects Hair

**Precondition:** Navigate to `#/dressup`

1. Observe the initial mermaid displayed (mermaid.svg — default character before any swap)
2. Note the body/skin/tail colors
3. Tap a color swatch (any non-default color) in the color row
4. **Expected:** Hair color shifts visibly. Body, skin, and tail colors remain unchanged
5. Tap a different color swatch
6. **Expected:** Hair shifts to the new hue. Body/skin/tail still unchanged
7. Open DevTools → Elements → find `#hair-group` inside `.mermaid-container`
8. **Expected:** `#hair-group` has `style="filter: hue-rotate(Xdeg)"` where X matches the swatch angle
9. Select the root `<svg>` element (parent of `#hair-group`)
10. **Expected:** Root SVG has NO filter style (empty or absent)

**Edge case:** Tap "undo" after changing color → hair reverts to previous hue, body/skin/tail still unchanged.

---

## Test Case 2: Hair Isolation After Character Swap

**Precondition:** Navigate to `#/dressup`

1. Tap a character thumbnail (e.g., mermaid-3) to swap characters
2. **Expected:** New character SVG loads, replacing previous mermaid
3. Note body/skin/tail colors of the new character
4. Tap a color swatch
5. **Expected:** Only hair changes color. Body/skin/tail unchanged on the swapped character
6. Tap another character thumbnail (e.g., mermaid-7)
7. **Expected:** Character swaps again. Previous hue-rotate is cleared — new character shows default colors
8. Apply a color swatch to mermaid-7
9. **Expected:** Only mermaid-7's hair shifts

---

## Test Case 3: "Color This!" Button Visible and Styled

**Precondition:** Navigate to `#/dressup`

1. Scroll the dress-up view if needed
2. **Expected:** A prominent "🎨 Color This!" button is visible below the color swatch row
3. **Expected:** Button has coral/orange gradient background, rounded corners, large touch target (min 60px height)
4. Tap and hold the button (without releasing)
5. **Expected:** Button shows a press/scale effect

---

## Test Case 4: "Color This!" Navigates to Coloring Canvas (Default Character)

**Precondition:** Navigate to `#/dressup`. Do NOT swap characters.

1. Tap the "🎨 Color This!" button
2. **Expected:** URL changes to `#/coloring?character=mermaid-1` (default character)
3. **Expected:** Coloring canvas appears with a B&W mermaid outline loaded
4. **Expected:** The outline is a recognizable mermaid shape (head, hair, tail, fins visible as white regions with black outlines)
5. Check Network tab in DevTools
6. **Expected:** Request for `assets/svg/dressup-coloring/mermaid-1-outline.svg` with 200 status

---

## Test Case 5: "Color This!" Navigates with Selected Character

**Precondition:** Navigate to `#/dressup`

1. Tap character thumbnail for mermaid-3
2. **Expected:** mermaid-3 loads in the display area
3. Tap the "🎨 Color This!" button
4. **Expected:** URL changes to `#/coloring?character=mermaid-3`
5. **Expected:** Coloring canvas loads with mermaid-3's outline SVG
6. Check Network tab
7. **Expected:** Request for `assets/svg/dressup-coloring/mermaid-3-outline.svg` with 200 status

Repeat with mermaid-9:
1. Navigate back to `#/dressup`
2. Tap character thumbnail for mermaid-9
3. Tap "🎨 Color This!"
4. **Expected:** URL is `#/coloring?character=mermaid-9`, canvas loads mermaid-9's outline

---

## Test Case 6: Coloring Canvas Functionality on Dress-Up Outline

**Precondition:** Navigate to `#/dressup`, select any character, tap "🎨 Color This!"

1. **Expected:** Coloring canvas is displayed with the outline SVG rendered
2. Select a color from the coloring palette
3. Tap inside a white region of the outline (e.g., the body area)
4. **Expected:** Flood-fill colors the tapped region with the selected color, bounded by the black outlines
5. Select a different color
6. Tap a different white region (e.g., the tail)
7. **Expected:** That region fills with the new color; previously colored region unchanged

---

## Test Case 7: Back Button Returns to Dress-Up

**Precondition:** From dress-up, tap "🎨 Color This!" to enter the character coloring view

1. **Expected:** A "Back to Dress Up" (or ←) back button is visible
2. Tap the back button
3. **Expected:** Navigates to `#/dressup`
4. **Expected:** Dress-up view loads with the character gallery and color swatches visible

---

## Test Case 8: All 9 Outline Assets Load

**Precondition:** Access to the file system or DevTools

For each character ID 1 through 9:
1. Navigate directly to `#/coloring?character=mermaid-{N}` (replace {N} with 1–9)
2. **Expected:** Coloring canvas loads without errors
3. **Expected:** A mermaid outline is visible on the canvas (not blank, not broken)
4. Check console for errors
5. **Expected:** No console errors related to SVG loading

---

## Test Case 9: Error Handling — Missing Outline SVG

**Precondition:** DevTools open with Network and Console tabs

1. Navigate to `#/coloring?character=mermaid-999` (non-existent character)
2. **Expected:** An error message is displayed in the app (`.error` div) — not a blank canvas
3. **Expected:** `console.error` logged with the failed SVG URL
4. **Expected:** No unhandled exceptions / white screen

---

## Test Case 10: Hair Group Present in All SVGs

**Verification via DevTools or CLI:**

1. For each mermaid SVG (`mermaid.svg` + `dressup/mermaid-{1-9}.svg`):
   - Open the SVG source
   - **Expected:** Contains exactly one `<g id="hair-group">` element
   - **Expected:** The `<g id="hair-group">` wraps exactly 2 `<path>` elements that have `clip-path="url(#hair-clip)"`
   - **Expected:** No non-hair paths inside the group

CLI shortcut:
```bash
for f in frontend/assets/svg/mermaid.svg frontend/assets/svg/dressup/mermaid-{1..9}.svg; do
  count=$(grep -c 'id="hair-group"' "$f")
  echo "$f: hair-group count=$count"
done
```
**Expected:** All 10 files show `count=1`
