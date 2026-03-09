/**
 * Coloring page state management: tap-to-fill, color palette, undo stack.
 *
 * Pure state + operations module -- no DOM event listeners wired here.
 * Event wiring happens in app.js when the coloring UI is built (Plan 02).
 *
 * Mirrors the structure of dressup.js but with separate state lifecycle.
 */

// Color palette -- 10 preset swatches, child-friendly (same as dressup.js,
// duplicated per research recommendation: separate state lifecycles)
export const COLORS = [
  "#7ec8c8", // ocean teal
  "#c4a7d7", // lavender
  "#ff69b4", // hot pink (default selected)
  "#ffd700", // gold
  "#87ceeb", // sky blue
  "#98fb98", // pale green
  "#ff6347", // tomato red
  "#dda0dd", // plum
  "#ffa07a", // light salmon
  "#40e0d0", // turquoise
];

// Coloring page metadata -- id, label, and file path for each page
export const COLORING_PAGES = [
  { id: "page-1-ocean", label: "Ocean Mermaid", file: "assets/svg/coloring/page-1-ocean.svg" },
  { id: "page-2-castle", label: "Mermaid Castle", file: "assets/svg/coloring/page-2-castle.svg" },
  { id: "page-3-seahorse", label: "Seahorse Friend", file: "assets/svg/coloring/page-3-seahorse.svg" },
  { id: "page-4-coral", label: "Coral Reef", file: "assets/svg/coloring/page-4-coral.svg" },
];

// -- State --------------------------------------------------------------------

export const state = {
  selectedColor: COLORS[2], // hot pink default
  currentPageId: null,
};

// -- Internal -----------------------------------------------------------------

const undoStack = [];
const MAX_UNDO = 30;

/**
 * Push an undo closure onto the stack. Cap at MAX_UNDO items.
 */
function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }
}

/**
 * Get fillable child elements from a region group.
 * Returns path, circle, ellipse, rect elements whose fill is not "none".
 */
function getFillableElements(regionGroup) {
  return Array.from(
    regionGroup.querySelectorAll("path, circle, ellipse, rect")
  ).filter((el) => {
    const fill = el.getAttribute("fill");
    return fill && fill !== "none";
  });
}

// -- Exported operations ------------------------------------------------------

/**
 * Fill all fillable children of a region group with the given color.
 * Captures previous fills and pushes an undo closure.
 *
 * @param {Element} regionGroup - A <g data-region="..."> SVG element
 * @param {string} color - CSS color string (e.g. "#ff69b4")
 */
export function fillRegion(regionGroup, color) {
  const elements = getFillableElements(regionGroup);
  if (elements.length === 0) return;

  // Capture previous fills for undo
  const previousFills = elements.map((el) => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));

  // Apply new color
  elements.forEach((el) => {
    el.setAttribute("fill", color);
  });

  // Push undo closure that restores previous fills
  pushUndo(() => {
    previousFills.forEach(({ element, fill }) => {
      element.setAttribute("fill", fill);
    });
  });
}

/**
 * Pop the last command from the undo stack and execute it.
 * No-op if the stack is empty.
 */
export function undo() {
  const cmd = undoStack.pop();
  if (cmd) cmd.undo();
}

/**
 * Set the currently selected color.
 *
 * @param {string} color - CSS color string
 */
export function setSelectedColor(color) {
  state.selectedColor = color;
}

/**
 * Get the currently selected color.
 *
 * @returns {string} The current selected color
 */
export function getSelectedColor() {
  return state.selectedColor;
}

/**
 * Reset all coloring state to defaults.
 * Clears undo stack, resets selected color to hot pink, clears current page.
 */
export function resetColoringState() {
  undoStack.length = 0;
  state.selectedColor = COLORS[2]; // hot pink default
  state.currentPageId = null;
}
