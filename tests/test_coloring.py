"""End-to-end Playwright tests for coloring requirements (COLR-01 through COLR-04).

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
All tests exercise the UI in the coloring view, not JS functions directly.

These tests will FAIL until Plan 02 wires the coloring UI into app.js.
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


def _open_first_page(coloring_page: Page) -> Page:
    """Helper: click first gallery thumbnail to open a coloring page."""
    coloring_page.locator(".gallery-thumb").first.click()
    coloring_page.wait_for_timeout(300)
    return coloring_page


class TestColoringGallery:
    """COLR-01: Gallery shows thumbnails and clicking one opens a coloring page."""

    def test_gallery_shows_thumbnails(self, coloring_page: Page):
        """Navigate to #/coloring. Assert .gallery-thumb buttons exist with count >= 4."""
        thumbs = coloring_page.locator(".gallery-thumb")
        assert thumbs.count() >= 4, f"Expected >= 4 gallery thumbnails, got {thumbs.count()}"
        # Each button should have a data-page attribute
        for i in range(thumbs.count()):
            attr = thumbs.nth(i).get_attribute("data-page")
            assert attr is not None, f"Thumbnail {i} missing data-page attribute"

    def test_thumbnail_opens_page(self, coloring_page: Page):
        """Click the first .gallery-thumb. Assert .coloring-view becomes visible with inlined SVG data-region elements."""
        coloring_page.locator(".gallery-thumb").first.click()
        coloring_page.wait_for_timeout(300)
        view = coloring_page.locator(".coloring-view")
        expect(view).to_be_visible()
        regions = coloring_page.locator(".coloring-view [data-region]")
        assert regions.count() >= 1, f"Expected data-region elements in coloring SVG, got {regions.count()}"


class TestColoringFill:
    """COLR-02: Tapping a region fills it with the selected color."""

    def test_tap_region_fills_color(self, coloring_page: Page):
        """Open a page, select a color, tap a region. Assert fill changed."""
        _open_first_page(coloring_page)
        # Click a color swatch to select a color
        swatch = coloring_page.locator(".color-swatch").first
        swatch_color = swatch.get_attribute("data-color")
        swatch.click()
        coloring_page.wait_for_timeout(200)
        # Click a data-region element
        region = coloring_page.locator(".coloring-view [data-region]").first
        region.click()
        coloring_page.wait_for_timeout(200)
        # Assert the region's child path fill changed to the selected color
        fill = coloring_page.evaluate("""
            (() => {
                const region = document.querySelector('.coloring-view [data-region]');
                if (!region) return null;
                const fillable = region.querySelector('path[fill]:not([fill="none"]), circle[fill]:not([fill="none"]), ellipse[fill]:not([fill="none"]), rect[fill]:not([fill="none"])');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)
        assert fill == swatch_color, f"Expected fill {swatch_color}, got {fill}"


class TestColoringPalette:
    """COLR-03: Color swatches are visible and change the active selection."""

    def test_swatches_visible(self, coloring_page: Page):
        """Open a page. Assert .color-swatch buttons exist with count >= 8."""
        _open_first_page(coloring_page)
        swatches = coloring_page.locator(".color-swatch")
        assert swatches.count() >= 8, f"Expected >= 8 color swatches, got {swatches.count()}"

    def test_swatch_changes_selection(self, coloring_page: Page):
        """Click swatch 0 and fill a region, then click swatch 3 and fill another region. Verify different colors applied."""
        _open_first_page(coloring_page)
        swatches = coloring_page.locator(".color-swatch")
        regions = coloring_page.locator(".coloring-view [data-region]")

        # Click swatch at index 0, fill first region
        swatch0_color = swatches.nth(0).get_attribute("data-color")
        swatches.nth(0).click()
        coloring_page.wait_for_timeout(200)
        regions.nth(0).click()
        coloring_page.wait_for_timeout(200)

        # Read fill of first region
        fill0 = coloring_page.evaluate("""
            (() => {
                const region = document.querySelectorAll('.coloring-view [data-region]')[0];
                if (!region) return null;
                const fillable = region.querySelector('path[fill]:not([fill="none"]), circle[fill]:not([fill="none"]), ellipse[fill]:not([fill="none"]), rect[fill]:not([fill="none"])');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)
        assert fill0 == swatch0_color, f"Expected fill {swatch0_color}, got {fill0}"

        # Click swatch at index 3, fill second region
        swatch3_color = swatches.nth(3).get_attribute("data-color")
        swatches.nth(3).click()
        coloring_page.wait_for_timeout(200)
        regions.nth(1).click()
        coloring_page.wait_for_timeout(200)

        # Read fill of second region
        fill1 = coloring_page.evaluate("""
            (() => {
                const region = document.querySelectorAll('.coloring-view [data-region]')[1];
                if (!region) return null;
                const fillable = region.querySelector('path[fill]:not([fill="none"]), circle[fill]:not([fill="none"]), ellipse[fill]:not([fill="none"]), rect[fill]:not([fill="none"])');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)
        assert fill1 == swatch3_color, f"Expected fill {swatch3_color}, got {fill1}"


class TestColoringUndo:
    """COLR-04: Undo button reverts the last color fill."""

    def test_undo_reverts_fill(self, coloring_page: Page):
        """Fill a region then undo. Assert fill reverts to the initial value."""
        _open_first_page(coloring_page)

        # Record initial fill of first region (should be white)
        initial_fill = coloring_page.evaluate("""
            (() => {
                const region = document.querySelector('.coloring-view [data-region]');
                if (!region) return null;
                const fillable = region.querySelector('path[fill], circle[fill], ellipse[fill], rect[fill]');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)

        # Click a color swatch then fill the region
        swatch = coloring_page.locator(".color-swatch").first
        swatch.click()
        coloring_page.wait_for_timeout(200)
        coloring_page.locator(".coloring-view [data-region]").first.click()
        coloring_page.wait_for_timeout(200)

        # Verify fill changed
        changed_fill = coloring_page.evaluate("""
            (() => {
                const region = document.querySelector('.coloring-view [data-region]');
                if (!region) return null;
                const fillable = region.querySelector('path[fill]:not([fill="none"]), circle[fill]:not([fill="none"]), ellipse[fill]:not([fill="none"]), rect[fill]:not([fill="none"])');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)
        assert changed_fill != initial_fill, f"Fill did not change after click: still {changed_fill}"

        # Click undo
        coloring_page.locator(".undo-btn").click()
        coloring_page.wait_for_timeout(200)

        # Verify fill reverted
        restored_fill = coloring_page.evaluate("""
            (() => {
                const region = document.querySelector('.coloring-view [data-region]');
                if (!region) return null;
                const fillable = region.querySelector('path[fill], circle[fill], ellipse[fill], rect[fill]');
                return fillable ? fillable.getAttribute('fill') : null;
            })()
        """)
        assert restored_fill == initial_fill, f"Expected {initial_fill} after undo, got {restored_fill}"
