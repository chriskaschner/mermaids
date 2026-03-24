# M003: Mermaid Art Rework

**Vision:** A web-based creative activity app for a 6-year-old, themed entirely around mermaids.

## Success Criteria


## Slices

- [x] **S01: Dress Up Art Rework** `risk:medium` `depends:[]`
  > After this: Rework the art generation pipeline from "each variant is a full character" to "one base body + swappable isolated parts. Fix hair paths that bleed beyond their visible region causing hue-rotate to recolor the entire character.
- [x] **S02: Coloring Art Rework** `risk:medium` `depends:[S01]`
  > After this: unit tests prove Coloring Art Rework works
- [x] **S03: Cleanup & Stability** `risk:medium` `depends:[S02]`
  > After this: unit tests prove Cleanup & Stability works
