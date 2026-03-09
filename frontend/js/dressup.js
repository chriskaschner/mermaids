/**
 * Dress-up state management: part swapping, color recoloring, undo stack,
 * completion detection, and UI wiring (initDressUp).
 *
 * Manages the mermaid SVG variant system where all part variants live in
 * <defs> and <use> elements reference the active variant per category.
 */

import { triggerCelebration } from "./sparkle.js";

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
  lastPartCategory: "tail", // tracks last non-color category for recoloring
  colors: {}, // { "tail-1": "#ff69b4", ... } per-variant color overrides
};

const undoStack = [];
const MAX_UNDO = 30;
let celebrated = false;

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
 * Recolor the currently active variant in the last-selected part category.
 * Modifies fill attributes directly on the source <g> in <defs>.
 * Stores color override in state.colors[variantId].
 * Pushes undo that restores previous per-element fills.
 *
 * When the color tab is active, we recolor the part from the most recently
 * selected part category (tail/hair/acc).
 */
export function recolorActivePart(color) {
  // Use lastPartCategory if activeCategory is "color"
  const category =
    state.activeCategory === "color"
      ? state.lastPartCategory || "tail"
      : state.activeCategory;

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
 * Triggers celebration sparkle on first completion. Resets celebrated flag
 * if any part returns to default.
 */
export function checkCompletion() {
  const isComplete =
    state.tail !== "tail-1" &&
    state.hair !== "hair-1" &&
    state.acc !== "acc-none";

  if (isComplete && !celebrated) {
    celebrated = true;
    const svgRoot = document.getElementById("mermaid-svg");
    if (svgRoot) {
      triggerCelebration(svgRoot);
    }
  } else if (!isComplete) {
    celebrated = false;
  }

  return isComplete;
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
  state.lastPartCategory = "tail";
  state.colors = {};
  undoStack.length = 0;
  celebrated = false;
  // Clear original colors cache
  Object.keys(originalColorsMap).forEach((key) => delete originalColorsMap[key]);
}

// -- UI wiring ----------------------------------------------------------------

/**
 * Render option buttons for a given category into the #options-row.
 * For tail/hair/acc: creates .option-btn buttons with small preview SVGs.
 * For color: creates .color-swatch buttons for each COLORS entry.
 */
function renderOptions(category) {
  const row = document.getElementById("options-row");
  if (!row) return;
  row.innerHTML = "";

  if (category === "color") {
    COLORS.forEach((color) => {
      const btn = document.createElement("button");
      btn.className = "color-swatch";
      btn.setAttribute("data-color", color);
      btn.setAttribute("aria-label", `Color ${color}`);
      btn.style.background = color;
      btn.style.touchAction = "manipulation";
      btn.addEventListener("click", () => {
        recolorActivePart(color);
      });
      row.appendChild(btn);
    });
    return;
  }

  const variants = PARTS[category];
  if (!variants) return;

  variants.forEach((variantId) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.setAttribute("data-variant", variantId);
    btn.setAttribute("aria-label", variantId);

    // Mark currently selected
    if (state[category] === variantId) {
      btn.classList.add("selected");
    }

    // Create a small preview icon for each variant
    btn.innerHTML = getVariantPreviewSVG(category, variantId);

    btn.addEventListener("click", () => {
      swapPart(category, variantId);
      // Update selected state on all option buttons
      row.querySelectorAll(".option-btn").forEach((b) => {
        b.classList.toggle("selected", b.getAttribute("data-variant") === variantId);
      });
    });
    row.appendChild(btn);
  });
}

/**
 * Return a small inline SVG preview icon for a variant.
 * These are simplified 24x24 shapes, not the full variant art.
 */
function getVariantPreviewSVG(category, variantId) {
  const previews = {
    "tail-1": '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12,2 Q8,10 6,16 Q10,20 12,18 Q14,20 18,16 Q16,10 12,2Z" fill="#7ec8c8"/></svg>',
    "tail-2": '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12,2 Q6,10 5,16 Q8,19 10,17 Q11,19 12,18 Q13,19 14,17 Q16,19 19,16 Q18,10 12,2Z" fill="#7ec8c8"/></svg>',
    "tail-3": '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12,2 Q9,10 8,14 L4,22 Q8,18 12,16 Q16,18 20,22 L16,14 Q15,10 12,2Z" fill="#7ec8c8"/></svg>',
    "hair-1": '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="10" r="6" fill="#c4a7d7"/><path d="M6,10 Q4,16 5,20" stroke="#c4a7d7" stroke-width="2" fill="none"/><path d="M18,10 Q20,16 19,20" stroke="#c4a7d7" stroke-width="2" fill="none"/></svg>',
    "hair-2": '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="10" r="6" fill="#c4a7d7"/><path d="M6,8 Q5,12 7,14" stroke="#c4a7d7" stroke-width="3" fill="none"/><path d="M18,8 Q19,12 17,14" stroke="#c4a7d7" stroke-width="3" fill="none"/></svg>',
    "hair-3": '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="10" r="6" fill="#c4a7d7"/><path d="M7,12 Q6,16 7,20" stroke="#c4a7d7" stroke-width="3" fill="none" stroke-dasharray="2 2"/><circle cx="7" cy="21" r="2" fill="#ffd700"/></svg>',
    "acc-none": '<svg width="24" height="24" viewBox="0 0 24 24"><line x1="6" y1="6" x2="18" y2="18" stroke="#ccc" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="6" x2="6" y2="18" stroke="#ccc" stroke-width="2" stroke-linecap="round"/></svg>',
    "acc-1": '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M4,16 L4,8 L8,12 L12,6 L16,12 L20,8 L20,16Z" fill="#ffd700"/></svg>',
    "acc-2": '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" fill="#ff69b4"/><circle cx="8" cy="8" r="3" fill="#ff69b4"/><circle cx="16" cy="8" r="3" fill="#ff69b4"/><circle cx="8" cy="16" r="3" fill="#ff69b4"/><circle cx="16" cy="16" r="3" fill="#ff69b4"/><circle cx="12" cy="12" r="2" fill="#ffd700"/></svg>',
    "acc-3": '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12,2 L13.5,8 L20,8 L14.5,12 L16,18 L12,14 L8,18 L9.5,12 L4,8 L10.5,8Z" fill="#ff6347"/></svg>',
  };
  return previews[variantId] || "";
}

/**
 * Initialize dress-up UI event listeners on the selection panel.
 * Call AFTER the selection panel HTML is in the DOM.
 */
export function initDressUp() {
  // Wire category tab clicks
  document.querySelectorAll(".cat-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const category = tab.getAttribute("data-category");
      state.activeCategory = category;

      // Track last part category for color recoloring
      if (category !== "color") {
        state.lastPartCategory = category;
      }

      // Update active class on tabs
      document.querySelectorAll(".cat-tab").forEach((t) => {
        t.classList.toggle("active", t === tab);
      });

      // Repopulate options row
      renderOptions(category);
    });
  });

  // Wire undo button
  const undoBtn = document.querySelector(".undo-btn");
  if (undoBtn) {
    undoBtn.addEventListener("click", () => {
      undo();
      // Refresh selected states on option buttons if showing a part category
      const cat = state.activeCategory;
      if (cat !== "color") {
        const row = document.getElementById("options-row");
        if (row) {
          row.querySelectorAll(".option-btn").forEach((btn) => {
            btn.classList.toggle(
              "selected",
              btn.getAttribute("data-variant") === state[cat]
            );
          });
        }
      }
    });
  }

  // Show tail options by default on load
  renderOptions("tail");
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
