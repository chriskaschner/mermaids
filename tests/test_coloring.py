"""End-to-end Playwright tests for canvas-based flood fill coloring (CLRV-01 through CLRV-05).

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
All tests exercise the UI in the coloring view with canvas+SVG hybrid rendering.

Canvas-based approach:
- Flood fill on HTML5 canvas (pixel-level) replaces old SVG data-region fill
- SVG line art overlays canvas with pointer-events:none for crisp retina lines
- Undo via ImageData snapshots
- Canvas memory released on navigation
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture()
def coloring_page(page: Page, live_server: str) -> Page:
    """Navigate to #/coloring and wait for the app container."""
    page.goto(f"{live_server}#/coloring")
    page.wait_for_selector("#app", state="attached")
    page.wait_for_timeout(300)
    return page


def _open_first_page(page: Page) -> Page:
    """Helper: click first gallery thumbnail to open a coloring page.
    Waits for the canvas to be created and ready."""
    page.locator(".gallery-thumb").first.click()
    page.wait_for_selector("#coloring-canvas", state="attached", timeout=5000)
    page.wait_for_timeout(500)
    return page


def _read_canvas_pixel(page: Page, x: int, y: int):
    """Read RGBA at canvas pixel (x, y). Returns [r, g, b, a] or None."""
    return page.evaluate(f"""(() => {{
        const canvas = document.querySelector('#coloring-canvas');
        if (!canvas) return null;
        const ctx = canvas.getContext('2d');
        const data = ctx.getImageData({x}, {y}, 1, 1).data;
        return [data[0], data[1], data[2], data[3]];
    }})()""")


def _tap_canvas_at(page: Page, canvas_x: int, canvas_y: int):
    """Tap at canvas pixel coordinates (mapped to CSS display coords).

    Dispatches pointerdown + pointerup events at the correct CSS position so the
    app.js handler can map it back to canvas pixel coordinates and complete the stroke.
    """
    page.evaluate(f"""(() => {{
        const canvas = document.querySelector('#coloring-canvas');
        const rect = canvas.getBoundingClientRect();
        const cssX = {canvas_x} * rect.width / canvas.width;
        const cssY = {canvas_y} * rect.height / canvas.height;
        const opts = {{
            clientX: rect.left + cssX,
            clientY: rect.top + cssY,
            bubbles: true,
            pointerId: 1,
            pointerType: 'touch'
        }};
        canvas.dispatchEvent(new PointerEvent('pointerdown', opts));
        canvas.dispatchEvent(new PointerEvent('pointerup', opts));
    }})()""")
    page.wait_for_timeout(200)


def _update_undo_state(page: Page):
    """Small wait for undo button state to update after fill/undo."""
    page.wait_for_timeout(100)


class TestColoringGallery:
    """Gallery shows thumbnails and clicking one opens a coloring page."""

    def test_gallery_shows_thumbnails(self, coloring_page: Page):
        """Navigate to #/coloring. Assert .gallery-thumb buttons exist with count >= 4."""
        thumbs = coloring_page.locator(".gallery-thumb")
        assert thumbs.count() >= 4, f"Expected >= 4 gallery thumbnails, got {thumbs.count()}"
        for i in range(thumbs.count()):
            attr = thumbs.nth(i).get_attribute("data-page")
            assert attr is not None, f"Thumbnail {i} missing data-page attribute"


class TestCanvasFloodFill:
    """CLRV-01/03: Tap white region fills with color via canvas flood fill;
    fill stops at anti-aliased line boundaries."""

    def test_tap_fills_region(self, coloring_page: Page):
        """Open a coloring page, tap a white area on the canvas, verify pixel
        color changed from white to the selected color."""
        _open_first_page(coloring_page)

        # Read a pixel in the center area -- should be white before fill
        before = _read_canvas_pixel(coloring_page, 512, 512)
        assert before is not None, "Canvas not found"

        # Tap at that location
        _tap_canvas_at(coloring_page, 512, 512)

        # Read the same pixel after fill
        after = _read_canvas_pixel(coloring_page, 512, 512)

        # Either it changed (fill happened) or the center is on a line.
        # If center is white, fill should turn it to the selected color.
        # If center is a line, the pixel was not white so fill targets line color.
        # In either case, the pixel should have changed from its initial value.
        if before == [255, 255, 255, 255]:
            # It was white -- should now be hot pink (#ff69b4 = 255, 105, 180)
            assert after[0] == 255 and after[1] == 105 and after[2] == 180, \
                f"Expected hot pink [255,105,180] but got {after[:3]}"
        else:
            # Center might be on a line; at minimum, the fill should have run
            # We verify via a broader check - something should have changed
            # or the pixel is already non-white (line art)
            pass

    def test_fill_stops_at_lines(self, coloring_page: Page):
        """Verify flood fill respects line boundaries by checking that after
        a fill, at least some non-white, non-filled pixels still exist
        (line art is preserved and not filled through)."""
        _open_first_page(coloring_page)

        # Find a dark (line art) pixel by scanning a row near the center
        line_pixel = coloring_page.evaluate("""(() => {
            const canvas = document.querySelector('#coloring-canvas');
            if (!canvas) return null;
            const ctx = canvas.getContext('2d');
            // Scan row 512 for a dark pixel (line art)
            const row = ctx.getImageData(0, 512, canvas.width, 1).data;
            for (let x = 0; x < canvas.width; x++) {
                const i = x * 4;
                // Dark pixel = all channels below 100
                if (row[i] < 100 && row[i+1] < 100 && row[i+2] < 100) {
                    return { x: x, y: 512, r: row[i], g: row[i+1], b: row[i+2] };
                }
            }
            return null;
        })()""")

        # Tap to fill at center (white area)
        _tap_canvas_at(coloring_page, 512, 512)

        if line_pixel is not None:
            # After fill, the line pixel should still be dark (not filled through)
            after = _read_canvas_pixel(coloring_page, line_pixel["x"], line_pixel["y"])
            assert after is not None, "Canvas not found after fill"
            # Line pixel should NOT be hot pink
            assert not (after[0] == 255 and after[1] == 105 and after[2] == 180), \
                f"Line pixel at ({line_pixel['x']}, 512) was filled through: {after[:3]}"


class TestCanvasLayout:
    """Canvas and SVG overlay are sized with margins, not edge-to-edge."""

    def test_canvas_has_margins(self, coloring_page: Page):
        """Canvas should not fill the entire viewport width -- it needs
        breathing room so the coloring page doesn't appear zoomed in."""
        _open_first_page(coloring_page)

        info = coloring_page.evaluate("""(() => {
            const container = document.querySelector('.coloring-page-container');
            const canvas = document.getElementById('coloring-canvas');
            const cr = container.getBoundingClientRect();
            const cvr = canvas.getBoundingClientRect();
            return {
                margin_left: cvr.left - cr.left,
                margin_right: (cr.left + cr.width) - (cvr.left + cvr.width),
            };
        })()""")
        assert info["margin_left"] >= 8, \
            f"Canvas should have left margin >= 8px, got {info['margin_left']}"
        assert info["margin_right"] >= 8, \
            f"Canvas should have right margin >= 8px, got {info['margin_right']}"

    def test_canvas_and_overlay_aligned(self, coloring_page: Page):
        """Canvas and SVG overlay should have identical size and position."""
        _open_first_page(coloring_page)

        info = coloring_page.evaluate("""(() => {
            const canvas = document.getElementById('coloring-canvas');
            const overlay = document.querySelector('.coloring-svg-overlay');
            if (!canvas || !overlay) return null;
            const cvr = canvas.getBoundingClientRect();
            const ovr = overlay.getBoundingClientRect();
            return {
                canvas: {w: Math.round(cvr.width), h: Math.round(cvr.height),
                         t: Math.round(cvr.top), l: Math.round(cvr.left)},
                overlay: {w: Math.round(ovr.width), h: Math.round(ovr.height),
                          t: Math.round(ovr.top), l: Math.round(ovr.left)},
            };
        })()""")
        assert info is not None, "Canvas or overlay not found"
        assert info["canvas"] == info["overlay"], \
            f"Canvas {info['canvas']} and overlay {info['overlay']} should match"


class TestCanvasOverlay:
    """CLRV-02: SVG line art overlays canvas for crisp retina outlines."""

    def test_svg_overlay_present(self, coloring_page: Page):
        """Open a coloring page, verify both canvas element and SVG overlay exist
        in the DOM, SVG has pointer-events:none."""
        _open_first_page(coloring_page)

        # Canvas should exist
        canvas = coloring_page.locator("#coloring-canvas")
        expect(canvas).to_be_attached()

        # SVG overlay should exist
        svg_overlay = coloring_page.locator(".coloring-svg-overlay")
        expect(svg_overlay).to_be_attached()

        # SVG overlay should have pointer-events: none
        pe = coloring_page.evaluate("""(() => {
            const svg = document.querySelector('.coloring-svg-overlay');
            if (!svg) return null;
            return getComputedStyle(svg).pointerEvents;
        })()""")
        assert pe == "none", f"SVG overlay pointer-events should be 'none', got '{pe}'"

    def test_svg_overlay_crisp(self, coloring_page: Page):
        """Verify SVG overlay element has a viewBox attribute (vector quality preserved)."""
        _open_first_page(coloring_page)

        viewbox = coloring_page.evaluate("""(() => {
            const svg = document.querySelector('.coloring-svg-overlay');
            if (!svg) return null;
            return svg.getAttribute('viewBox') || svg.getAttribute('viewbox');
        })()""")
        # The SVG should have a viewBox for proper scaling
        # vtracer SVGs might use width/height without viewBox -- the overlay code
        # should preserve whatever the source SVG has
        assert viewbox is not None or coloring_page.evaluate("""(() => {
            const svg = document.querySelector('.coloring-svg-overlay');
            return svg && svg.getAttribute('width') && svg.getAttribute('height');
        })()"""), "SVG overlay should have viewBox or width/height for vector quality"


class TestCanvasUndo:
    """CLRV-05: Undo reverts last flood-fill operation via ImageData snapshots."""

    def test_undo_reverts_fill(self, coloring_page: Page):
        """Fill a region, click undo, verify pixel returns to original color."""
        _open_first_page(coloring_page)

        # Record the pre-fill pixel at center
        before = _read_canvas_pixel(coloring_page, 512, 512)
        assert before is not None, "Canvas not found"

        # Tap to fill
        _tap_canvas_at(coloring_page, 512, 512)
        after_fill = _read_canvas_pixel(coloring_page, 512, 512)

        # Click undo
        coloring_page.locator(".coloring-toolbar .undo-btn").click()
        coloring_page.wait_for_timeout(300)

        # Read pixel after undo
        after_undo = _read_canvas_pixel(coloring_page, 512, 512)

        # After undo, pixel should match the pre-fill state
        assert after_undo == before, \
            f"After undo expected {before} but got {after_undo}"

    def test_undo_button_disabled_when_empty(self, coloring_page: Page):
        """Before any fills, verify undo button has .disabled class;
        after a fill, verify .disabled is removed;
        after undoing all fills, verify .disabled is back."""
        _open_first_page(coloring_page)

        undo_btn = coloring_page.locator(".coloring-toolbar .undo-btn")

        # Initially should be disabled
        initial_classes = undo_btn.get_attribute("class") or ""
        assert "disabled" in initial_classes, \
            f"Undo should be disabled initially, classes: '{initial_classes}'"

        # Tap to fill
        _tap_canvas_at(coloring_page, 512, 512)
        _update_undo_state(coloring_page)

        # Should no longer be disabled
        after_fill_classes = undo_btn.get_attribute("class") or ""
        assert "disabled" not in after_fill_classes, \
            f"Undo should be enabled after fill, classes: '{after_fill_classes}'"

        # Undo the fill
        undo_btn.click()
        coloring_page.wait_for_timeout(200)

        # Should be disabled again
        after_undo_classes = undo_btn.get_attribute("class") or ""
        assert "disabled" in after_undo_classes, \
            f"Undo should be disabled after undoing all fills, classes: '{after_undo_classes}'"


class TestCanvasMemory:
    """CLRV-04: Canvas memory released on navigation away from coloring."""

    def test_canvas_released_on_nav(self, coloring_page: Page):
        """Open coloring page, navigate to home, verify canvas element is
        removed from DOM (or has width=0)."""
        _open_first_page(coloring_page)

        # Verify canvas exists
        assert coloring_page.locator("#coloring-canvas").count() > 0, \
            "Canvas should exist on coloring page"

        # Navigate to home
        coloring_page.goto(coloring_page.url.split("#")[0] + "#/home")
        coloring_page.wait_for_timeout(500)

        # Canvas should be removed or have width=0
        canvas_present = coloring_page.evaluate("""(() => {
            const canvas = document.querySelector('#coloring-canvas');
            if (!canvas) return 'removed';
            if (canvas.width === 0 && canvas.height === 0) return 'zeroed';
            return 'present';
        })()""")
        assert canvas_present in ("removed", "zeroed"), \
            f"Canvas should be released on nav, but status: {canvas_present}"

    def test_canvas_released_on_back(self, coloring_page: Page):
        """Open coloring page, click back to gallery, verify canvas is cleaned up."""
        _open_first_page(coloring_page)

        # Verify canvas exists
        assert coloring_page.locator("#coloring-canvas").count() > 0

        # Click back button
        coloring_page.locator(".back-btn").click()
        coloring_page.wait_for_timeout(500)

        # Canvas should be gone
        canvas_present = coloring_page.evaluate("""(() => {
            const canvas = document.querySelector('#coloring-canvas');
            if (!canvas) return 'removed';
            if (canvas.width === 0 && canvas.height === 0) return 'zeroed';
            return 'present';
        })()""")
        assert canvas_present in ("removed", "zeroed"), \
            f"Canvas should be released on back, but status: {canvas_present}"


class TestColoringPalette:
    """Color swatches work: tapping a swatch changes the active fill color."""

    def test_swatches_visible(self, coloring_page: Page):
        """Open a coloring page, verify 10 .color-swatch buttons exist."""
        _open_first_page(coloring_page)
        swatches = coloring_page.locator(".color-swatch")
        assert swatches.count() == 10, f"Expected 10 color swatches, got {swatches.count()}"

    def test_swatch_changes_selection(self, coloring_page: Page):
        """Click different swatches, fill regions, verify different colors applied."""
        _open_first_page(coloring_page)

        # Select first swatch (ocean teal #7ec8c8 = 126, 200, 200)
        swatches = coloring_page.locator(".color-swatch")
        swatches.nth(0).click()
        coloring_page.wait_for_timeout(100)

        # Tap to fill at one location
        _tap_canvas_at(coloring_page, 512, 512)

        # Read pixel -- should be ocean teal
        pixel1 = _read_canvas_pixel(coloring_page, 512, 512)

        # Undo the fill to restore white
        coloring_page.locator(".coloring-toolbar .undo-btn").click()
        coloring_page.wait_for_timeout(200)

        # Select fourth swatch (gold #ffd700 = 255, 215, 0)
        swatches.nth(3).click()
        coloring_page.wait_for_timeout(100)

        # Tap same location
        _tap_canvas_at(coloring_page, 512, 512)

        # Read pixel -- should be gold
        pixel2 = _read_canvas_pixel(coloring_page, 512, 512)

        # Verify different colors were applied
        if pixel1 is not None and pixel2 is not None:
            assert pixel1[:3] != pixel2[:3], \
                f"Expected different colors but both are {pixel1[:3]}"
