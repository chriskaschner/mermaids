/**
 * Sparkle particle effect for SVG tap feedback.
 *
 * Creates small gold circles at the tap point that fade out via CSS animation.
 */

const SVG_NS = "http://www.w3.org/2000/svg";
const SPARKLE_COUNT = 6;
const SPARKLE_LIFETIME_MS = 600;
const SPARKLE_SPREAD = 20;

/**
 * Get SVG-local coordinates from a pointer event.
 * @param {SVGSVGElement} svgRoot
 * @param {PointerEvent} event
 * @returns {{x: number, y: number}}
 */
function getSVGPoint(svgRoot, event) {
  const pt = svgRoot.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const ctm = svgRoot.getScreenCTM();
  if (ctm) {
    const svgPt = pt.matrixTransform(ctm.inverse());
    return { x: svgPt.x, y: svgPt.y };
  }
  return { x: pt.x, y: pt.y };
}

/**
 * Create sparkle particles at the tap point within an SVG.
 * @param {SVGElement} svgRoot - The root <svg> element to append sparkles to.
 * @param {PointerEvent|MouseEvent} event - The pointer/mouse event with clientX/clientY.
 */
export function triggerSparkle(svgRoot, event) {
  const { x, y } = getSVGPoint(svgRoot, event);

  for (let i = 0; i < SPARKLE_COUNT; i++) {
    const circle = document.createElementNS(SVG_NS, "circle");
    const offsetX = (Math.random() - 0.5) * 2 * SPARKLE_SPREAD;
    const offsetY = (Math.random() - 0.5) * 2 * SPARKLE_SPREAD;
    const radius = 2 + Math.random() * 3;

    circle.setAttribute("cx", String(x + offsetX));
    circle.setAttribute("cy", String(y + offsetY));
    circle.setAttribute("r", String(radius));
    circle.setAttribute("fill", "gold");
    circle.classList.add("sparkle");

    svgRoot.appendChild(circle);

    setTimeout(() => {
      if (circle.parentNode) {
        circle.parentNode.removeChild(circle);
      }
    }, SPARKLE_LIFETIME_MS);
  }
}
