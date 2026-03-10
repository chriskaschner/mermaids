/**
 * Canvas-based coloring state management: flood fill, color palette, undo stack.
 *
 * Pure state + operations module -- no DOM event listeners wired here.
 * Event wiring happens in app.js when the coloring UI is built (Plan 02).
 *
 * Canvas lifecycle:
 *   initColoringCanvas() -> handleCanvasTap() x N -> releaseCanvas()
 *
 * Undo via ImageData snapshots (capped at MAX_UNDO).
 */

import { floodFill, hexToRgb } from "./floodfill.js";

// -- Constants ----------------------------------------------------------------

const MAX_UNDO = 30;
const FILL_TOLERANCE = 32;
const CANVAS_SIZE = 1024;

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

/** Module-level canvas and context references. */
let _canvas = null;
let _ctx = null;

/** Undo stack: array of ImageData snapshots. */
const undoStack = [];

// -- Exported operations ------------------------------------------------------

/**
 * Initialize a canvas for coloring by rasterizing an SVG onto it.
 *
 * Creates a canvas element (CANVAS_SIZE x CANVAS_SIZE), gets a 2d context
 * with willReadFrequently: true, fills white, loads the SVG as an Image,
 * and draws it onto the canvas.
 *
 * @param {string} svgUrl - URL of the SVG file to rasterize
 * @param {HTMLElement} container - DOM element to append the canvas to
 * @returns {Promise<{canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D}>}
 */
export async function initColoringCanvas(svgUrl, container) {
  // Clean up any previous canvas
  releaseCanvas();

  const canvas = document.createElement("canvas");
  canvas.width = CANVAS_SIZE;
  canvas.height = CANVAS_SIZE;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });

  // White background (flood fill needs a base color)
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Rasterize the SVG onto the canvas
  const img = new Image();
  img.src = svgUrl;
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

  // Store module-level references
  _canvas = canvas;
  _ctx = ctx;

  // Append to container
  if (container) {
    container.appendChild(canvas);
  }

  return { canvas, ctx };
}

/**
 * Handle a tap on the coloring canvas at the given pixel coordinates.
 *
 * Pushes a pre-fill ImageData snapshot onto the undo stack, runs flood fill
 * at (canvasX, canvasY) with the selected color, and puts the modified
 * ImageData back onto the canvas.
 *
 * @param {number} canvasX - X coordinate in canvas pixel space
 * @param {number} canvasY - Y coordinate in canvas pixel space
 */
export function handleCanvasTap(canvasX, canvasY) {
  if (!_canvas || !_ctx) return;

  // Push pre-fill snapshot for undo
  const snapshot = _ctx.getImageData(0, 0, _canvas.width, _canvas.height);
  undoStack.push(snapshot);
  if (undoStack.length > MAX_UNDO) {
    undoStack.shift();
  }

  // Get current image data, run flood fill, put it back
  const imageData = _ctx.getImageData(0, 0, _canvas.width, _canvas.height);
  floodFill(imageData, Math.floor(canvasX), Math.floor(canvasY), state.selectedColor, FILL_TOLERANCE);
  _ctx.putImageData(imageData, 0, 0);
}

/**
 * Pop the last ImageData snapshot from the undo stack and restore it.
 * No-op if the stack is empty.
 */
export function undo() {
  const snapshot = undoStack.pop();
  if (snapshot && _ctx) {
    _ctx.putImageData(snapshot, 0, 0);
  }
}

/**
 * Check whether there are any undo entries available.
 *
 * @returns {boolean} true if undo stack has entries
 */
export function canUndo() {
  return undoStack.length > 0;
}

/**
 * Release the coloring canvas to free memory.
 *
 * Sets canvas width/height to 0, removes it from the DOM, nulls module-level
 * references, and clears the undo stack. Critical for iPad Safari memory safety.
 */
export function releaseCanvas() {
  if (_canvas) {
    _canvas.width = 0;
    _canvas.height = 0;
    if (_canvas.parentNode) {
      _canvas.parentNode.removeChild(_canvas);
    }
  }
  _canvas = null;
  _ctx = null;
  undoStack.length = 0;
}

/**
 * Set the currently selected color.
 *
 * @param {string} color - CSS hex color string (e.g. "#ff69b4")
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
 * Test helper: set canvas and context directly (bypasses SVG loading).
 * Only used by unit tests to inject a synthetic canvas.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {CanvasRenderingContext2D} ctx
 */
export function _setTestCanvas(canvas, ctx) {
  releaseCanvas();
  _canvas = canvas;
  _ctx = ctx;
}
