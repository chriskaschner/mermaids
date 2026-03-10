"""Unit tests for floodfill.js -- scanline flood fill algorithm.

Uses Playwright to load a minimal test harness that imports floodfill.js as an
ES module, creates synthetic canvas ImageData, and exercises floodFill/hexToRgb
through the browser JS engine.

Tests verify:
- hexToRgb parses hex color strings to [r, g, b] arrays
- Flood fill spreads within a bounded white region
- Flood fill stops at black line edges with tolerance=32
- Flood fill is a no-op when start pixel already matches fill color
- Flood fill handles out-of-bounds / line-pixel start gracefully
"""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="module")
def _harness_page(browser):
    """Create a single browser context + page that loads the test harness."""
    context = browser.new_context()
    page = context.new_page()
    # Serve the floodfill module via a minimal data URL that imports it
    # We need a real server because ES modules require HTTP, not file://
    yield page
    context.close()


@pytest.fixture()
def js_page(page: Page, live_server: str) -> Page:
    """Navigate to a blank page on the live server for JS evaluation."""
    page.goto(f"{live_server}")
    page.wait_for_timeout(200)
    return page


class TestHexToRgb:
    """hexToRgb converts hex color strings to [r, g, b] arrays."""

    def test_hot_pink(self, js_page: Page):
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                return mod.hexToRgb('#ff69b4');
            })()
        """)
        assert result == [255, 105, 180]

    def test_black(self, js_page: Page):
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                return mod.hexToRgb('#000000');
            })()
        """)
        assert result == [0, 0, 0]

    def test_white(self, js_page: Page):
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                return mod.hexToRgb('#ffffff');
            })()
        """)
        assert result == [255, 255, 255]

    def test_ocean_teal(self, js_page: Page):
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                return mod.hexToRgb('#7ec8c8');
            })()
        """)
        assert result == [126, 200, 200]


class TestFloodFillBasic:
    """Flood fill spreads within bounded regions and stops at edges."""

    def test_fill_white_region_inside_black_border(self, js_page: Page):
        """Create a 10x10 white canvas with a 1px black border. Fill center.
        Assert interior pixels are filled and border pixels are untouched."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                // Create a 10x10 ImageData: white background
                const w = 10, h = 10;
                const data = new Uint8ClampedArray(w * h * 4);
                // Fill all white
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255; data[i+3] = 255;
                }
                // Draw a 1px black border (row 0, row 9, col 0, col 9)
                for (let x = 0; x < w; x++) {
                    for (let y = 0; y < h; y++) {
                        if (x === 0 || x === w-1 || y === 0 || y === h-1) {
                            const idx = (y * w + x) * 4;
                            data[idx] = 0; data[idx+1] = 0; data[idx+2] = 0; data[idx+3] = 255;
                        }
                    }
                }
                const imageData = new ImageData(data, w, h);

                // Fill center (5,5) with hot pink
                mod.floodFill(imageData, 5, 5, '#ff69b4', 32);

                // Check center pixel is hot pink
                const ci = (5 * w + 5) * 4;
                const centerColor = [imageData.data[ci], imageData.data[ci+1], imageData.data[ci+2]];

                // Check border pixel is still black
                const bi = (0 * w + 0) * 4;
                const borderColor = [imageData.data[bi], imageData.data[bi+1], imageData.data[bi+2]];

                // Check another interior pixel
                const ii = (3 * w + 3) * 4;
                const interiorColor = [imageData.data[ii], imageData.data[ii+1], imageData.data[ii+2]];

                return { centerColor, borderColor, interiorColor };
            })()
        """)
        assert result["centerColor"] == [255, 105, 180], f"Center not filled: {result['centerColor']}"
        assert result["borderColor"] == [0, 0, 0], f"Border was modified: {result['borderColor']}"
        assert result["interiorColor"] == [255, 105, 180], f"Interior not filled: {result['interiorColor']}"

    def test_fill_stops_at_anti_aliased_edges(self, js_page: Page):
        """Create a region with gray (anti-aliased) edges between white and black.
        With tolerance=32, fill should stop at pixels far from white."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                // 10x10 white canvas with a gray vertical line at x=5
                // Gray value 128 -- differs from white (255) by 127, well above tolerance 32
                const w = 10, h = 10;
                const data = new Uint8ClampedArray(w * h * 4);
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255; data[i+3] = 255;
                }
                // Gray vertical line at x=5
                for (let y = 0; y < h; y++) {
                    const idx = (y * w + 5) * 4;
                    data[idx] = 128; data[idx+1] = 128; data[idx+2] = 128; data[idx+3] = 255;
                }
                const imageData = new ImageData(data, w, h);

                // Fill at (2, 5) -- left side of the gray line
                mod.floodFill(imageData, 2, 5, '#ff69b4', 32);

                // Left side pixel should be filled
                const li = (5 * w + 2) * 4;
                const leftColor = [imageData.data[li], imageData.data[li+1], imageData.data[li+2]];

                // Right side pixel should NOT be filled (still white)
                const ri = (5 * w + 7) * 4;
                const rightColor = [imageData.data[ri], imageData.data[ri+1], imageData.data[ri+2]];

                // Gray line pixel should NOT be filled
                const gi = (5 * w + 5) * 4;
                const grayColor = [imageData.data[gi], imageData.data[gi+1], imageData.data[gi+2]];

                return { leftColor, rightColor, grayColor };
            })()
        """)
        assert result["leftColor"] == [255, 105, 180], f"Left side not filled: {result['leftColor']}"
        assert result["rightColor"] == [255, 255, 255], f"Right side was filled (bleed): {result['rightColor']}"
        assert result["grayColor"] == [128, 128, 128], f"Gray line was modified: {result['grayColor']}"

    def test_noop_when_start_matches_fill_color(self, js_page: Page):
        """If the start pixel is already the fill color, nothing changes."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                // 5x5 canvas filled with hot pink
                const w = 5, h = 5;
                const data = new Uint8ClampedArray(w * h * 4);
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = 255; data[i+1] = 105; data[i+2] = 180; data[i+3] = 255;
                }
                const imageData = new ImageData(data, w, h);

                // Fill with same color -- should be no-op
                mod.floodFill(imageData, 2, 2, '#ff69b4', 32);

                // Verify pixel unchanged
                const ci = (2 * w + 2) * 4;
                return [imageData.data[ci], imageData.data[ci+1], imageData.data[ci+2]];
            })()
        """)
        assert result == [255, 105, 180]

    def test_start_on_line_pixel_fills_minimally(self, js_page: Page):
        """If start pixel is on a black line, only matching-color pixels fill."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                // 5x5 canvas: white bg with a single black pixel at (2,2)
                const w = 5, h = 5;
                const data = new Uint8ClampedArray(w * h * 4);
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255; data[i+3] = 255;
                }
                // Black pixel at (2,2)
                const bi = (2 * w + 2) * 4;
                data[bi] = 0; data[bi+1] = 0; data[bi+2] = 0; data[bi+3] = 255;

                const imageData = new ImageData(data, w, h);

                // Fill starting at the black pixel
                mod.floodFill(imageData, 2, 2, '#ff69b4', 32);

                // The black pixel should become hot pink (it was target, fill replaces it)
                const after = [imageData.data[bi], imageData.data[bi+1], imageData.data[bi+2]];

                // Adjacent white pixels should NOT be filled (they don't match black within tolerance)
                const adj = (2 * w + 3) * 4;
                const adjColor = [imageData.data[adj], imageData.data[adj+1], imageData.data[adj+2]];

                return { targetPixel: after, adjacentPixel: adjColor };
            })()
        """)
        assert result["targetPixel"] == [255, 105, 180], f"Target pixel not filled: {result['targetPixel']}"
        assert result["adjacentPixel"] == [255, 255, 255], f"Adjacent pixel was filled: {result['adjacentPixel']}"

    def test_out_of_bounds_coordinates_safe(self, js_page: Page):
        """Calling floodFill with coordinates outside the canvas does not throw."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                const w = 5, h = 5;
                const data = new Uint8ClampedArray(w * h * 4);
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255; data[i+3] = 255;
                }
                const imageData = new ImageData(data, w, h);

                // Out of bounds -- should not throw
                try {
                    mod.floodFill(imageData, -1, -1, '#ff69b4', 32);
                    mod.floodFill(imageData, 100, 100, '#ff69b4', 32);
                    return 'ok';
                } catch (e) {
                    return 'error: ' + e.message;
                }
            })()
        """)
        assert result == "ok", f"Out of bounds threw: {result}"

    def test_default_tolerance_exported(self, js_page: Page):
        """DEFAULT_TOLERANCE constant is exported with value 32."""
        result = js_page.evaluate("""
            (async () => {
                const mod = await import('./js/floodfill.js');
                return mod.DEFAULT_TOLERANCE;
            })()
        """)
        assert result == 32
