---
created: 2026-03-12T11:50:23.647Z
title: Persist dressed mermaid to coloring view
area: ui
files:
  - frontend/js/dressup.js
  - frontend/js/coloring.js
---

## Problem

Currently the mermaid you customize with accessories in the dress-up view is independent from the one shown in the coloring view. Users expect the mermaid they dressed up to carry over into the coloring activity so they can color the same character they just accessorized.

## Solution

When transitioning from dress-up to coloring, pass the current accessory state (selected items, positions) to the coloring view so it renders the same dressed-up mermaid. May require shared state or an event bus between the two views.
