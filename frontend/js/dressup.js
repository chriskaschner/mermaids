/**
 * Dress-up character gallery: 9 diverse mermaid characters displayed in a
 * flat gallery. Tap a character to select it. Color swatches apply a
 * hue-rotate CSS filter to shift the character's colors.
 *
 * Each character is a standalone pre-generated SVG (mermaid-1..9).
 */

import { triggerCelebration } from "./sparkle.js?v=14";

// Character IDs
export const CHARACTERS = [
  "mermaid-1", "mermaid-2", "mermaid-3",
  "mermaid-4", "mermaid-5", "mermaid-6",
  "mermaid-7", "mermaid-8", "mermaid-9",
];

// Color palette -- each color maps to a hue-rotate angle
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

// State
export const state = {
  activeCharacter: "mermaid-1",
  currentRotation: 0,
};

const undoStack = [];
const MAX_UNDO = 30;
let celebrated = false;

// Cache for fetched SVG text
const characterSVGCache = new Map();

// -- Core operations ----------------------------------------------------------

async function fetchCharacterSVG(characterId) {
  if (characterSVGCache.has(characterId)) {
    return characterSVGCache.get(characterId);
  }
  const resp = await fetch(`assets/svg/dressup/${characterId}.svg`);
  const text = await resp.text();
  characterSVGCache.set(characterId, text);
  return text;
}

/**
 * Extract hue (0-360) from a hex color string.
 */
function hexToHue(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  if (d === 0) return 0;
  let h;
  if (max === r) h = ((g - b) / d) % 6;
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  h = Math.round(h * 60);
  if (h < 0) h += 360;
  return h;
}

/**
 * Select a character. Fetches and displays its SVG.
 */
export async function selectCharacter(characterId) {
  if (state.activeCharacter === characterId) return;

  const prevId = state.activeCharacter;
  const prevRotation = state.currentRotation;
  state.activeCharacter = characterId;
  state.currentRotation = 0;

  const svgText = await fetchCharacterSVG(characterId);
  const container = document.querySelector(".dressup-view .mermaid-container");
  if (!container) return;
  container.innerHTML = svgText;

  // Clear any hue filter from previous character
  const svgEl = container.querySelector("svg");
  if (svgEl) svgEl.style.filter = "";

  // Update gallery selection
  document.querySelectorAll(".char-btn").forEach((btn) => {
    btn.classList.toggle("selected", btn.getAttribute("data-character") === characterId);
  });

  pushUndo(async () => {
    state.activeCharacter = prevId;
    state.currentRotation = prevRotation;
    const prevSvg = await fetchCharacterSVG(prevId);
    const c = document.querySelector(".dressup-view .mermaid-container");
    if (c) {
      c.innerHTML = prevSvg;
      const svg = c.querySelector("svg");
      if (svg && prevRotation) svg.style.filter = `hue-rotate(${prevRotation}deg)`;
    }
    document.querySelectorAll(".char-btn").forEach((btn) => {
      btn.classList.toggle("selected", btn.getAttribute("data-character") === prevId);
    });
  });

  checkCompletion();
}

/**
 * Apply a hue-rotate filter to the displayed character SVG.
 */
export function recolorActivePart(color) {
  const container = document.querySelector(".dressup-view .mermaid-container");
  if (!container) return;
  const svgEl = container.querySelector("svg");
  if (!svgEl) return;

  const prevRotation = state.currentRotation;
  const hue = hexToHue(color);
  state.currentRotation = hue;

  svgEl.style.filter = hue === 0 ? "" : `hue-rotate(${hue}deg)`;

  pushUndo(() => {
    state.currentRotation = prevRotation;
    svgEl.style.filter = prevRotation === 0 ? "" : `hue-rotate(${prevRotation}deg)`;
  });
}

export async function undo() {
  const cmd = undoStack.pop();
  if (cmd) await cmd.undo();
}

export function checkCompletion() {
  const isComplete = state.activeCharacter !== "mermaid-1";

  if (isComplete && !celebrated) {
    celebrated = true;
    const container = document.querySelector(".dressup-view .mermaid-container");
    const svgRoot = container ? container.querySelector("svg") : null;
    if (svgRoot) {
      triggerCelebration(svgRoot);
    }
  } else if (!isComplete) {
    celebrated = false;
  }

  return isComplete;
}

export function resetState() {
  state.activeCharacter = "mermaid-1";
  state.currentRotation = 0;
  undoStack.length = 0;
  celebrated = false;
}

// -- UI wiring ----------------------------------------------------------------

export async function initDressUp() {
  // Wire character gallery buttons
  document.querySelectorAll(".char-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const characterId = btn.getAttribute("data-character");
      await selectCharacter(characterId);
    });
  });

  // Wire color swatches
  document.querySelectorAll(".color-swatch").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const color = btn.getAttribute("data-color");
      recolorActivePart(color);
    });
  });

  // Wire undo
  const undoBtn = document.querySelector(".undo-btn");
  if (undoBtn) {
    undoBtn.addEventListener("click", async (e) => {
      e.stopPropagation();
      await undo();
    });
  }
}

// -- Internal helpers ---------------------------------------------------------

function pushUndo(fn) {
  undoStack.push({ undo: fn });
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }
}
