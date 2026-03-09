/**
 * Sparkle particle effect for SVG tap feedback.
 *
 * Creates small gold circles at the tap point that fade out via CSS animation.
 */

const SVG_NS = "http://www.w3.org/2000/svg";
const SPARKLE_COUNT = 6;
const SPARKLE_LIFETIME_MS = 600;
const SPARKLE_SPREAD = 20;

const CELEBRATION_COLORS = ["gold", "#ff69b4", "#87ceeb", "#dda0dd"];
const CELEBRATION_POSITIONS = [
  { x: 200, y: 80 },  // head
  { x: 200, y: 250 }, // body
  { x: 200, y: 500 }, // tail
];
const CELEBRATION_PARTICLES = 12;
const CELEBRATION_SPREAD = 80;
const CELEBRATION_LIFETIME_MS = 1000;
const CELEBRATION_STAGGER_MS = 150;

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

/**
 * Multi-burst celebration sparkle across the mermaid SVG.
 * Fires 3 staggered bursts (head, body, tail) with 12 particles each.
 * @param {SVGElement} svgRoot - The root <svg> element to append sparkles to.
 */
export function triggerCelebration(svgRoot) {
  CELEBRATION_POSITIONS.forEach((pos, i) => {
    setTimeout(() => {
      for (let j = 0; j < CELEBRATION_PARTICLES; j++) {
        const circle = document.createElementNS(SVG_NS, "circle");
        const offsetX = (Math.random() - 0.5) * CELEBRATION_SPREAD;
        const offsetY = (Math.random() - 0.5) * CELEBRATION_SPREAD;
        const radius = 3 + Math.random() * 5;

        circle.setAttribute("cx", String(pos.x + offsetX));
        circle.setAttribute("cy", String(pos.y + offsetY));
        circle.setAttribute("r", String(radius));
        circle.setAttribute("fill", CELEBRATION_COLORS[j % CELEBRATION_COLORS.length]);
        circle.classList.add("sparkle", "celebration");

        svgRoot.appendChild(circle);

        setTimeout(() => {
          if (circle.parentNode) {
            circle.parentNode.removeChild(circle);
          }
        }, CELEBRATION_LIFETIME_MS);
      }
    }, i * CELEBRATION_STAGGER_MS);
  });
}
