/**
 * Dress-up character gallery: 9 diverse mermaid characters displayed in a
 * flat gallery. Tap a character to select it. Color swatches recolor the
 * active character. Includes skin tone colors for inclusive customization.
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

// Color palette -- fun colors + skin tones for inclusive customization
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

export const SKIN_TONES = [
  "#FDDCB5", // light
  "#F5C5A3", // light-medium
  "#E8A97E", // medium
  "#D4915A", // medium-tan
  "#C07840", // brown
  "#8D5524", // deep brown
];

// State
export const state = {
  activeCharacter: "mermaid-1",
  colors: {},
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
 * Select a character. Fetches and displays its SVG.
 */
export async function selectCharacter(characterId) {
  if (state.activeCharacter === characterId) return;

  const prevId = state.activeCharacter;
  state.activeCharacter = characterId;

  const svgText = await fetchCharacterSVG(characterId);
  const container = document.querySelector(".dressup-view .mermaid-container");
  if (!container) return;
  container.innerHTML = svgText;

  // Update gallery selection
  document.querySelectorAll(".char-btn").forEach((btn) => {
    btn.classList.toggle("selected", btn.getAttribute("data-character") === characterId);
  });

  pushUndo(async () => {
    state.activeCharacter = prevId;
    const prevSvg = await fetchCharacterSVG(prevId);
    const c = document.querySelector(".dressup-view .mermaid-container");
    if (c) c.innerHTML = prevSvg;
    document.querySelectorAll(".char-btn").forEach((btn) => {
      btn.classList.toggle("selected", btn.getAttribute("data-character") === prevId);
    });
  });

  checkCompletion();
}

/**
 * Recolor paths in the currently displayed character SVG.
 */
export function recolorActivePart(color) {
  const svgRoot = document.getElementById("mermaid-svg");
  if (!svgRoot) return;

  const elements = getRecolorableElements(svgRoot);
  const previousFills = elements.map((el) => ({
    element: el,
    fill: el.getAttribute("fill"),
  }));

  elements.forEach((el) => {
    el.setAttribute("fill", color);
  });

  pushUndo(() => {
    previousFills.forEach(({ element, fill }) => {
      element.setAttribute("fill", fill);
    });
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
    const svgRoot = document.getElementById("mermaid-svg");
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
  state.colors = {};
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

function _isDark(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return r < 0x50 && g < 0x50 && b < 0x50;
}

function _isSkinTone(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return r > 0xD0 && g > 0x90 && g < 0xE0 && b > 0x70 && b < 0xD0 && r > g && g > b;
}

function _isNearWhite(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return r > 0xE8 && g > 0xE8 && b > 0xE8;
}

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
