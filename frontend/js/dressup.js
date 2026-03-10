/**
 * Dress-up state management: part swapping, color recoloring, undo stack,
 * completion detection, and UI wiring (initDressUp).
 *
 * Manages the mermaid SVG variant system where all part variants live in
 * <defs> and <use> elements reference the active variant per category.
 *
 * Previews are fetched from individual traced SVGs at runtime and displayed
 * at 48x48 inside 64x64 option buttons. Previews reflect color overrides.
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

// Cache for fetched preview SVG text (keyed by variantId)
const previewSVGCache = new Map();

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
 * Also updates the visible preview button for the recolored variant.
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

  // Update the preview button SVG if it is currently visible in the options row
  const row = document.getElementById("options-row");
  if (row) {
    const btn = row.querySelector(`.option-btn[data-variant="${variantId}"] svg`);
    if (btn) {
      applyColorToPreviewSVG(btn, color);
    }
  }

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

// -- Preview fetch and color sync ---------------------------------------------

/**
 * Fetch a variant's individual SVG file for use as a preview thumbnail.
 * Caches the original SVG text so repeated renders don't re-fetch.
 */
async function fetchVariantPreview(variantId) {
  if (previewSVGCache.has(variantId)) {
    return previewSVGCache.get(variantId);
  }
  const resp = await fetch(`assets/svg/dressup/${variantId}.svg`);
  const text = await resp.text();
  previewSVGCache.set(variantId, text);
  return text;
}

/**
 * Apply a color override to all fill-bearing elements within a preview SVG.
 * Reuses the same getFillBearingElements logic as the main defs recoloring.
 */
function applyColorToPreviewSVG(svgEl, color) {
  getFillBearingElements(svgEl).forEach((el) => {
    el.setAttribute("fill", color);
  });
}

// -- UI wiring ----------------------------------------------------------------

/**
 * Render option buttons for a given category into the #options-row.
 * For tail/hair/acc: creates .option-btn buttons with fetched preview SVGs.
 * For color: creates .color-swatch buttons for each COLORS entry.
 *
 * This is async because variant preview SVGs are fetched from individual files.
 */
async function renderOptions(category) {
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

  // Create all buttons first (synchronously) for instant layout
  const buttons = variants.map((variantId) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.setAttribute("data-variant", variantId);
    btn.setAttribute("aria-label", variantId);

    // Mark currently selected
    if (state[category] === variantId) {
      btn.classList.add("selected");
    }

    btn.addEventListener("click", () => {
      swapPart(category, variantId);
      // Update selected state on all option buttons
      row.querySelectorAll(".option-btn").forEach((b) => {
        b.classList.toggle("selected", b.getAttribute("data-variant") === variantId);
      });
    });

    row.appendChild(btn);
    return { btn, variantId };
  });

  // Fetch and insert preview SVGs (async)
  await Promise.all(
    buttons.map(async ({ btn, variantId }) => {
      if (variantId === "acc-none") {
        // Keep a simple X icon for the "none" accessory option
        btn.innerHTML =
          '<svg width="48" height="48" viewBox="0 0 48 48">' +
          '<line x1="12" y1="12" x2="36" y2="36" stroke="#ccc" stroke-width="3" stroke-linecap="round"/>' +
          '<line x1="36" y1="12" x2="12" y2="36" stroke="#ccc" stroke-width="3" stroke-linecap="round"/>' +
          "</svg>";
        return;
      }

      const svgText = await fetchVariantPreview(variantId);
      btn.innerHTML = svgText;

      // Configure the SVG element for consistent sizing
      const svgEl = btn.querySelector("svg");
      if (svgEl) {
        svgEl.setAttribute("width", "48");
        svgEl.setAttribute("height", "48");
        if (!svgEl.getAttribute("viewBox")) {
          svgEl.setAttribute("viewBox", "0 0 1024 1024");
        }

        // Apply saved color override to the preview
        const savedColor = state.colors[variantId];
        if (savedColor) {
          applyColorToPreviewSVG(svgEl, savedColor);
        }
      }
    })
  );
}

/**
 * Initialize dress-up UI event listeners on the selection panel.
 * Call AFTER the selection panel HTML is in the DOM.
 */
export async function initDressUp() {
  // Wire category tab clicks
  document.querySelectorAll(".cat-tab").forEach((tab) => {
    tab.addEventListener("click", async () => {
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

      // Repopulate options row (async for fetched previews)
      await renderOptions(category);
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
  await renderOptions("tail");
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
