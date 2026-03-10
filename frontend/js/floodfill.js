/**
 * Scanline flood fill algorithm with tolerance-based edge detection.
 *
 * Operates on raw ImageData typed arrays for maximum performance.
 * Uses iterative scanline approach (not recursive) to avoid stack overflow
 * on large canvas regions.
 *
 * @module floodfill
 */

/** Default color tolerance for anti-aliased edge detection. */
export const DEFAULT_TOLERANCE = 32;

/**
 * Parse a hex color string to an [r, g, b] array.
 *
 * @param {string} hex - CSS hex color (e.g. "#ff69b4")
 * @returns {number[]} [r, g, b] where each value is 0-255
 */
export function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/**
 * Scanline flood fill on ImageData.
 *
 * Fills connected pixels matching the target color (pixel at startX, startY)
 * with the given fill color. Stops at pixels that differ from target by more
 * than `tolerance` on any RGBA channel.
 *
 * Modifies `imageData.data` in place.
 *
 * @param {ImageData} imageData - Canvas image data to modify
 * @param {number} startX - X coordinate of fill start point
 * @param {number} startY - Y coordinate of fill start point
 * @param {string} fillColor - Hex color to fill with (e.g. "#ff69b4")
 * @param {number} tolerance - Per-channel tolerance (0-255), default 32
 * @param {number} [maxFillRatio=0.25] - Max fraction of canvas pixels to fill (leak guard)
 */
export function floodFill(imageData, startX, startY, fillColor, tolerance, maxFillRatio = 0.25) {
  const { data, width, height } = imageData;

  // Bounds check
  startX = Math.floor(startX);
  startY = Math.floor(startY);
  if (startX < 0 || startX >= width || startY < 0 || startY >= height) {
    return;
  }

  // Get target color (the color at the start pixel)
  const startIdx = (startY * width + startX) * 4;
  const targetR = data[startIdx];
  const targetG = data[startIdx + 1];
  const targetB = data[startIdx + 2];
  const targetA = data[startIdx + 3];

  // Parse fill color
  const [fr, fg, fb] = hexToRgb(fillColor);

  // If start pixel already matches fill color exactly, return early (no-op)
  if (
    data[startIdx] === fr &&
    data[startIdx + 1] === fg &&
    data[startIdx + 2] === fb &&
    data[startIdx + 3] === 255
  ) {
    return;
  }

  // Visited bitmap to prevent revisiting pixels
  const visited = new Uint8Array(width * height);

  /**
   * Check whether pixel at data index i matches the target color
   * within tolerance on each RGBA channel.
   */
  function colorMatch(i) {
    return (
      Math.abs(data[i] - targetR) <= tolerance &&
      Math.abs(data[i + 1] - targetG) <= tolerance &&
      Math.abs(data[i + 2] - targetB) <= tolerance &&
      Math.abs(data[i + 3] - targetA) <= tolerance
    );
  }

  // Pixel budget: abort fill if it exceeds maxFillRatio of total pixels
  // (indicates a leak through an open path). Save original data to restore.
  const totalPixels = width * height;
  const pixelBudget = Math.floor(totalPixels * maxFillRatio);
  let filledCount = 0;
  const backup = new Uint8ClampedArray(data);

  // Scanline stack: each entry is [x, y]
  const stack = [[startX, startY]];

  while (stack.length > 0) {
    let [x, y] = stack.pop();
    let pixIdx = y * width + x;

    // Scan left to find the start of this scanline segment
    while (
      x > 0 &&
      !visited[pixIdx - 1] &&
      colorMatch((y * width + (x - 1)) * 4)
    ) {
      x--;
      pixIdx--;
    }

    let spanAbove = false;
    let spanBelow = false;

    // Scan right across the scanline, filling pixels
    while (
      x < width &&
      !visited[pixIdx] &&
      colorMatch(pixIdx * 4)
    ) {
      const i = pixIdx * 4;
      data[i] = fr;
      data[i + 1] = fg;
      data[i + 2] = fb;
      data[i + 3] = 255;
      visited[pixIdx] = 1;
      filledCount++;

      // Leak guard: if we've filled too many pixels, revert everything
      if (filledCount > pixelBudget) {
        data.set(backup);
        return;
      }

      // Check pixel above
      if (y > 0) {
        const aboveIdx = pixIdx - width;
        const above = !visited[aboveIdx] && colorMatch(aboveIdx * 4);
        if (above && !spanAbove) {
          stack.push([x, y - 1]);
          spanAbove = true;
        } else if (!above) {
          spanAbove = false;
        }
      }

      // Check pixel below
      if (y < height - 1) {
        const belowIdx = pixIdx + width;
        const below = !visited[belowIdx] && colorMatch(belowIdx * 4);
        if (below && !spanBelow) {
          stack.push([x, y + 1]);
          spanBelow = true;
        } else if (!below) {
          spanBelow = false;
        }
      }

      x++;
      pixIdx++;
    }
  }
}
