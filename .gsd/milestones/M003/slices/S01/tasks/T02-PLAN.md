# T02: 08-dress-up-art-rework 02

**Slice:** S01 — **Milestone:** M003

## Description

Rework the dress-up frontend from "swap between full characters" to "swap individual parts independently." Add eyes as a new category tab. Change recoloring to apply per-part (active category only). Update E2E tests.

Purpose: The current UI treats each variant as a complete character -- clicking "hair-2" shows an entirely different mermaid, not just different hair. The new approach has one persistent body with hair/eyes/tail/acc swapping independently via separate `<use>` elements.

Output: Updated dressup.js (multi-part swap logic), app.js (5-tab UI), and passing E2E tests.

## Must-Haves

- [ ] "User sees one consistent mermaid body that stays the same across all part changes"
- [ ] "User can tap hair tab and swap between 3 hair styles while body/eyes/tail/acc stay unchanged"
- [ ] "User can tap eyes tab and swap between 3 eye styles while body/hair/tail/acc stay unchanged"
- [ ] "User can tap tail tab and swap between 3 tail styles while body/hair/eyes/acc stay unchanged"
- [ ] "Color swatch recolors only the active category's part, not the entire character"

## Files

- `frontend/js/dressup.js`
- `frontend/js/app.js`
- `tests/test_dressup.py`
