/**
 * Dress-up state management: part swapping, color recoloring, undo stack,
 * and completion detection.
 *
 * Manages the mermaid SVG variant system where all part variants live in
 * <defs> and <use> elements reference the active variant per category.
 */

// Part variant definitions
export const PARTS = {
  tail: ["tail-1", "tail-2", "tail-3"],
  hair: ["hair-1", "hair-2", "hair-3"],
  acc: ["acc-none", "acc-1", "acc-2", "acc-3"],
};

// Color palette -- 10 preset swatches, child-friendly
export const COLORS = [
  "#7ec8c8", // ocean teal (default tail)
  "#c4a7d7", // lavender (default hair)
  "#ff69b4", // hot pink
  "#ffd700", // gold
  "#87ceeb", // sky blue
  "#98fb98", // pale green
  "#ff6347", // tomato red
  "#dda0dd", // plum
  "#ffa07a", // light salmon
  "#40e0d0", // turquoise
];

// State -- source of truth for active parts and color overrides
export const state = {
  tail: "tail-1",
  hair: "hair-1",
  acc: "acc-none",
  activeCategory: "tail",
  colors: {}, // { "tail-1": "#ff69b4", ... } per-variant color overrides
};

const undoStack = [];
const MAX_UNDO = 30;

// Map of original fill arrays keyed by variantId, captured on first recolor
const originalColorsMap = {};

// -- Core operations ----------------------------------------------------------

/**
 * Swap the active variant for a category.
 * Changes the <use> href, tracks in state, pushes undo, re-applies color
 * override if one exists for the new variant, and checks completion.
 * No-op if the same variant is already selected.
 */
export function swapPart(category, variantId) {
  const useEl = document.getElementById(`active-${category}`);
  if (!useEl) return;

  const prevHref = useEl.getAttribute("href");
  const prevId = prevHref ? prevHref.slice(1) : null;
  if (prevId === variantId) return; // no-op

  useEl.setAttribute("href", `#${variantId}`);

  // Re-apply color override if one exists for the new variant
  const savedColor = state.colors[variantId];
  if (savedColor) {
    applyColorToSource(variantId, savedColor);
  }

  state[category] = variantId;

  pushUndo(() => {
    useEl.setAttribute("href", `#${prevId}`);
    state[category] = prevId;
    // Re-apply color override for the restored variant
    const prevColor = state.colors[prevId];
    if (prevColor) {
      applyColorToSource(prevId, prevColor);
    }
  });

  checkCompletion();
}

/**
 * Recolor the currently active variant in the active category.
 * Modifies fill attributes directly on the source <g> in <defs>.
 * Stores color override in state.colors[variantId].
 * Pushes undo that restores previous per-element fills.
 */
export function recolorActivePart(color) {
  const category = state.activeCategory;
  if (category === "color") return; // color tab has no "active part"

  const variantId = state[category];
  if (!variantId || variantId === "acc-none") return;

  const source = document.getElementById(variantId);
  if (!source) return;

  // Capture original fills on first recolor of this variant
  if (!originalColorsMap[variantId]) {
    originalColorsMap[variantId] = getOriginalColors(variantId);
  }

  // Capture current fills for undo (element-by-element)
  const elements = getFillBearingElements(source);
  const previousFills = elements.map((el) => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));
  const previousColorOverride = state.colors[variantId] || null;

  // Apply the new color
  applyColorToSource(variantId, color);
  state.colors[variantId] = color;

  pushUndo(() => {
    // Restore each element's previous fill
    previousFills.forEach(({ element, fill }) => {
      element.setAttribute("fill", fill);
    });
    // Restore the color override in state
    if (previousColorOverride) {
      state.colors[variantId] = previousColorOverride;
    } else {
      delete state.colors[variantId];
    }
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
 * Check if the mermaid is "complete" -- all categories have non-default
 * selections. Returns true if tail !== "tail-1" AND hair !== "hair-1"
 * AND acc !== "acc-none".
 *
 * Does NOT trigger celebration directly -- that is wired in the UI layer
 * (Plan 02).
 */
export function checkCompletion() {
  return (
    state.tail !== "tail-1" &&
    state.hair !== "hair-1" &&
    state.acc !== "acc-none"
  );
}

/**
 * Read original fill attributes from a variant's source <g> children.
 * Returns an array of {element, fill} for undo support.
 * Called lazily on first recolor of a variant.
 */
export function getOriginalColors(variantId) {
  const source = document.getElementById(variantId);
  if (!source) return [];
  return getFillBearingElements(source).map((el) => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));
}

/**
 * Reset state to defaults, clear undo stack and color overrides.
 * Useful when navigating away and back.
 */
export function resetState() {
  state.tail = "tail-1";
  state.hair = "hair-1";
  state.acc = "acc-none";
  state.activeCategory = "tail";
  state.colors = {};
  undoStack.length = 0;
  // Clear original colors cache
  Object.keys(originalColorsMap).forEach((key) => delete originalColorsMap[key]);
}

// -- Internal helpers ---------------------------------------------------------

/**
 * Apply a single color to all fill-bearing children of a source <g> in <defs>.
 * Skips elements with fill="none".
 */
function applyColorToSource(variantId, color) {
  const source = document.getElementById(variantId);
  if (!source) return;
  getFillBearingElements(source).forEach((el) => {
    el.setAttribute("fill", color);
  });
}

/**
 * Get all child elements that have a fill attribute that is not "none".
 * Targets path, circle, ellipse, rect elements.
 */
function getFillBearingElements(parentEl) {
  return Array.from(
    parentEl.querySelectorAll("path, circle, ellipse, rect")
  ).filter((el) => {
    const fill = el.getAttribute("fill");
    return fill && fill !== "none";
  });
}

/**
 * Push an undo function onto the stack. Cap at MAX_UNDO items.
 */
function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }
}
