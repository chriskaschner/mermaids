---
created: 2026-03-12T11:56:00.000Z
title: Flood fill loses edge boundaries after many taps
area: ui
files:
  - frontend/js/coloring.js
---

## Problem

On iPad Safari, after many taps in the coloring view, the flood fill starts filling everything -- it loses awareness of the outlines/edges and fills across boundaries. The more regions you fill, the worse it gets.

Possible causes:
- Anti-aliased outline pixels create semi-transparent boundaries that the fill tolerance eventually bleeds through
- Canvas compositing from repeated fills may alter boundary pixel colors
- Fill tolerance threshold too generous after colors layer on top of each other

## Solution

TBD -- needs investigation. Likely needs tighter tolerance, or a different approach to boundary detection (e.g., using the original outline layer as a persistent mask rather than checking current pixel colors).
