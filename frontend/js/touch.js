/**
 * SVG touch event handling with expanded hit areas.
 *
 * Uses event delegation on the SVG root to detect taps on [data-region] groups,
 * triggering sparkle feedback and a brief opacity pulse.
 */

import { triggerSparkle } from "./sparkle.js?v=14";

const PULSE_DURATION_MS = 200;

/**
 * Initialize touch handling on an SVG element.
 * @param {string} svgSelector - CSS selector for the SVG root element.
 */
export function initTouch(svgSelector) {
  const svg = document.querySelector(svgSelector);
  if (!svg) return;

  svg.addEventListener("pointerdown", (event) => {
    const region = event.target.closest("[data-region]");
    if (!region) return;

    // Sparkle effect at tap point
    triggerSparkle(svg, event);

    // Brief opacity pulse for immediate visual feedback (FOUN-04)
    region.style.opacity = "0.7";
    setTimeout(() => {
      region.style.opacity = "1.0";
    }, PULSE_DURATION_MS);
  });
}
