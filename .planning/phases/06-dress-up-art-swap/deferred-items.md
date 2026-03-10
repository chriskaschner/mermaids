# Deferred Items - Phase 06

## Pre-existing Test Failure

**test_e2e.py::TestTouchInteraction::test_tap_region_triggers_sparkle**

The AI-generated mermaid SVG has overlapping `<use>` regions -- the hair region visually overlaps and intercepts pointer events on the tail region. This causes Playwright's click() to fail because `<use href="#hair-1">` intercepts the click targeted at `[data-region="tail"]`.

This was already failing before Plan 02 changes (verified by stashing changes and re-running). The issue stems from the AI-generated SVG layout from Plan 01 where variant positioning causes overlap.

**Suggested fix:** Adjust the scale transform or position of variant groups in the assembled mermaid.svg to prevent overlap, or use `force: true` in the test click.
