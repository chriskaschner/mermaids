# T01: 08-dress-up-art-rework 01

**Slice:** S01 — **Milestone:** M003

## Description

Rework the art generation pipeline from "each variant is a full character" to "one base body + swappable isolated parts." Add eyes as a new category. Redesign region masks so hair, eyes, tail, and accessories do not overlap (fixes DEBT-03). Update SVG assembly to produce multi-layer stacked `<use>` structure.

Purpose: The current pipeline generates 9 full-character variants where each is a complete mermaid. The new approach generates 1 static base body + 12 isolated part variants (3 per category), assembled into an SVG with 5 `<use>` layers that can be swapped independently.

Output: Updated pipeline modules (prompts.py, edit.py, assemble.py) and passing tests.

## Must-Haves

- [ ] "Pipeline generates 1 base mermaid + 12 part variants (3 hair, 3 eyes, 3 tail, 3 acc)"
- [ ] "Region masks for hair, eyes, tail, and accessories do not overlap"
- [ ] "Assembled SVG has 5 stacked use elements (tail, body, hair, eyes, accessories) instead of 1"
- [ ] "Each use element references a part group in defs, not a full character"

## Files

- `src/mermaids/pipeline/prompts.py`
- `src/mermaids/pipeline/edit.py`
- `src/mermaids/pipeline/assemble.py`
- `tests/test_masks.py`
- `tests/test_assemble.py`
