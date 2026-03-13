/**
 * Dress-up character selection: swap individual parts independently via stacked
 * <use> elements, apply per-part recoloring, undo stack, completion detection.
 *
 * SVG structure (from assemble.py):
 *   <use id="active-tail" href="#tail-1" data-category="tail" />
 *   <use id="active-body" href="#body" />
 *   <use id="active-hair" href="#hair-1" data-category="hair" />
 *   <use id="active-eyes" href="#eye-1" data-category="eyes" />
 *   <use id="active-acc"  href="#acc-1"  data-category="acc"  />
 *
 * Each category has 3 variants in <defs>. swapPart() updates only the target
 * layer's href, leaving all other layers unchanged.
 *
 * Previews are fetched from individual traced SVGs and shown at 48x48.
 */

import { triggerCelebration } from "./sparkle.js?v=14";

// Part variant IDs per category
export const PARTS = {
  hair: ["hair-1", "hair-2", "hair-3"],
  eyes: ["eye-1", "eye-2", "eye-3"],
  tail: ["tail-1", "tail-2", "tail-3"],
  acc: ["acc-1", "acc-2", "acc-3"],
};

// Color palette -- 10 preset swatches, child-friendly
export const COLORS = [
  "#7ec8c8", // ocean teal
  "#c4a7d7", // lavender
  "#ff69b4", // hot pink
  "#ffd700", // gold
  "#87ceeb", // sky blue
  "#98fb98", // pale green
  "#ff6347", // tomato red
  "#dda0dd", // plum
  "#ffa07a", // light salmon
  "#40e0d0", // turquoise
];

// State -- source of truth for active parts and category
export const state = {
  hair: "hair-1",
  eyes: "eye-1",
  tail: "tail-1",
  acc: "acc-1",
  activeCategory: "hair", // Default to hair (first tab in UI order)
  lastPartCategory: "hair",
  colors: {}, // { "hair-1": "#ff69b4" } per-part color overrides
};

const undoStack = [];
const MAX_UNDO = 30;
let celebrated = false;

// Cache for fetched preview SVG text (keyed by variantId)
const previewSVGCache = new Map();

// -- Core operations ----------------------------------------------------------

/**
 * Swap the part for a specific category. Updates only that category's <use>
 * element href; all other layers remain unchanged.
 *
 * @param {string} category - "hair" | "eyes" | "tail" | "acc"
 * @param {string} variantId - e.g. "hair-2", "eye-3"
 */
export function swapPart(category, variantId) {
  const useEl = document.getElementById(`active-${category}`);
  if (!useEl) return;

  const prevHref = useEl.getAttribute("href");
  const prevVariantId = prevHref ? prevHref.slice(1) : null;
  if (prevVariantId === variantId) return; // no-op

  const prevStateValue = state[category];

  useEl.setAttribute("href", `#${variantId}`);
  state[category] = variantId;

  // Re-apply color override if one exists for the new variant
  const savedColor = state.colors[variantId];
  if (savedColor) {
    applyColorToSource(variantId, savedColor);
  }

  pushUndo(() => {
    useEl.setAttribute("href", `#${prevVariantId}`);
    state[category] = prevStateValue;
    const prevColor = state.colors[prevVariantId];
    if (prevColor) {
      applyColorToSource(prevVariantId, prevColor);
    }
  });

  checkCompletion();
}

/**
 * Recolor the currently active category's part.
 * Uses state.activeCategory; if on "color" tab, falls back to lastPartCategory.
 * Only recolors paths that are not outlines or skin tones.
 *
 * @param {string} color - hex color string e.g. "#ff69b4"
 */
export function recolorActivePart(color) {
  const category = state.activeCategory !== "color"
    ? state.activeCategory
    : state.lastPartCategory;

  const variantId = state[category];
  if (!variantId) return;

  const source = document.getElementById(variantId);
  if (!source) return;

  // Capture current fills for undo
  const elements = getRecolorableElements(source);
  const previousFills = elements.map((el) => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));
  const previousColorOverride = state.colors[variantId] || null;

  // Apply the new color
  applyColorToSource(variantId, color);
  state.colors[variantId] = color;

  // Update the preview button SVG if visible
  const row = document.getElementById("options-row");
  if (row) {
    const btn = row.querySelector(`.option-btn[data-variant="${variantId}"] svg`);
    if (btn) {
      applyColorToPreviewSVG(btn, color);
    }
  }

  pushUndo(() => {
    previousFills.forEach(({ element, fill }) => {
      element.setAttribute("fill", fill);
    });
    if (previousColorOverride) {
      state.colors[variantId] = previousColorOverride;
    } else {
      delete state.colors[variantId];
    }
  });
}

/**
 * Pop the last command from the undo stack and execute it.
 */
export function undo() {
  const cmd = undoStack.pop();
  if (cmd) cmd.undo();
}

/**
 * Check if the user has explored all 4 categories (selected at least one
 * non-default in each). Triggers celebration on first completion.
 */
export function checkCompletion() {
  const isComplete =
    state.hair !== "hair-1" &&
    state.eyes !== "eye-1" &&
    state.tail !== "tail-1" &&
    state.acc !== "acc-1";

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
 * Reset state to defaults, clear undo stack and color overrides.
 */
export function resetState() {
  state.hair = "hair-1";
  state.eyes = "eye-1";
  state.tail = "tail-1";
  state.acc = "acc-1";
  state.activeCategory = "hair";
  state.lastPartCategory = "hair";
  state.colors = {};
  undoStack.length = 0;
  celebrated = false;
}

// -- Preview fetch and color sync ---------------------------------------------

async function fetchVariantPreview(variantId) {
  if (previewSVGCache.has(variantId)) {
    return previewSVGCache.get(variantId);
  }
  const resp = await fetch(`assets/svg/dressup/${variantId}.svg`);
  const text = await resp.text();
  previewSVGCache.set(variantId, text);
  return text;
}

function applyColorToPreviewSVG(svgEl, color) {
  getRecolorableElements(svgEl).forEach((el) => {
    el.setAttribute("fill", color);
  });
}

// -- UI wiring ----------------------------------------------------------------

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
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        recolorActivePart(color);
      });
      row.appendChild(btn);
    });
    return;
  }

  const variants = PARTS[category];
  if (!variants) return;

  const buttons = variants.map((variantId) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.setAttribute("data-variant", variantId);
    btn.setAttribute("aria-label", variantId);

    if (state[category] === variantId) {
      btn.classList.add("selected");
    }

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      swapPart(category, variantId);
      row.querySelectorAll(".option-btn").forEach((b) => {
        b.classList.toggle("selected", b.getAttribute("data-variant") === variantId);
      });
    });

    row.appendChild(btn);
    return { btn, variantId };
  });

  await Promise.all(
    buttons.map(async ({ btn, variantId }) => {
      try {
        const svgText = await fetchVariantPreview(variantId);
        btn.innerHTML = svgText;

        const svgEl = btn.querySelector("svg");
        if (svgEl) {
          svgEl.setAttribute("width", "48");
          svgEl.setAttribute("height", "48");
          if (!svgEl.getAttribute("viewBox")) {
            svgEl.setAttribute("viewBox", "0 0 1024 1024");
          }

          const savedColor = state.colors[variantId];
          if (savedColor) {
            applyColorToPreviewSVG(svgEl, savedColor);
          }
        }
      } catch {
        // Preview fetch failed -- leave button without thumbnail (non-fatal)
      }
    })
  );
}

export async function initDressUp() {
  document.querySelectorAll(".cat-tab").forEach((tab) => {
    tab.addEventListener("click", async (e) => {
      e.stopPropagation();
      const category = tab.getAttribute("data-category");
      state.activeCategory = category;

      if (category !== "color") {
        state.lastPartCategory = category;
      }

      document.querySelectorAll(".cat-tab").forEach((t) => {
        t.classList.toggle("active", t === tab);
      });

      await renderOptions(category);
    });
  });

  const undoBtn = document.querySelector(".undo-btn");
  if (undoBtn) {
    undoBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      undo();
      const cat = state.activeCategory !== "color"
        ? state.activeCategory
        : state.lastPartCategory;
      const row = document.getElementById("options-row");
      if (row) {
        row.querySelectorAll(".option-btn").forEach((btn) => {
          btn.classList.toggle(
            "selected",
            btn.getAttribute("data-variant") === state[cat]
          );
        });
      }
    });
  }

  // Render the default "hair" options (matches first active tab in UI)
  await renderOptions("hair");
}

// -- Internal helpers ---------------------------------------------------------

/**
 * Apply a single color to recolorable elements of a source <g> in <defs>.
 * Skips outlines (dark fills) and skin tones to preserve character detail.
 */
function applyColorToSource(variantId, color) {
  const source = document.getElementById(variantId);
  if (!source) return;
  getRecolorableElements(source).forEach((el) => {
    el.setAttribute("fill", color);
  });
}

/**
 * Check if a hex color is a dark outline (all RGB < 0x50).
 */
function _isDark(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return r < 0x50 && g < 0x50 && b < 0x50;
}

/**
 * Check if a hex color is a skin tone (peachy/beige range).
 */
function _isSkinTone(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  // Skin tones: high red, moderate green, lower blue, warm hue
  return r > 0xD0 && g > 0x90 && g < 0xE0 && b > 0x70 && b < 0xD0 && r > g && g > b;
}

/**
 * Check if a hex color is near-white (all RGB > 0xE8).
 */
function _isNearWhite(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return r > 0xE8 && g > 0xE8 && b > 0xE8;
}

/**
 * Get child elements that have a fill suitable for recoloring.
 * Skips: fill="none", dark outlines, skin tones, near-white.
 */
function getRecolorableElements(parentEl) {
  return Array.from(
    parentEl.querySelectorAll("path, circle, ellipse, rect")
  ).filter((el) => {
    const fill = el.getAttribute("fill");
    if (!fill || fill === "none") return false;
    const hex = fill.trim();
    if (!hex.startsWith("#") || hex.length !== 7) return false;
    if (_isDark(hex)) return false;
    if (_isSkinTone(hex)) return false;
    if (_isNearWhite(hex)) return false;
    return true;
  });
}

function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }
}
