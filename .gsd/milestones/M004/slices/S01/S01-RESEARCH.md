# S01 Research: Dress-Up → Coloring Pipeline + Hair Path Fix

**Milestone:** M004  
**Slice:** S01  
**Gathered:** 2026-03-23  
**Requirements owned:** PIPE-01, PIPE-02, PIPE-03, HAIR-01  

## Summary

S01 has three independent work streams:

1. **HAIR-01** — clipPath already exists in all 9 SVGs (clips at y=310). Missing: `<g id="hair-group">` wrapper + dressup.js targeting `#hair-group` instead of root SVG.
2. **PIPE-03** — New pipeline: `COLORING_BASE_PROMPT + DRESSUP_CHARACTERS[i]['prompt_detail']`, trace `simplify=True`, deploy to `frontend/assets/svg/dressup-coloring/`.
3. **PIPE-01/PIPE-02** — "Color This!" button in `renderDressUp()`, hash-param routing `#/coloring?character=mermaid-3`, new `renderColoringForCharacter()`.

All three tasks are independent. T02 (outlines) must be complete before T03 (routing) can be fully verified. 104 tests exist; target 106-107 after S01.
