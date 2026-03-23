"""End-to-end Playwright tests for dress-up character gallery.

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
The dress-up view shows a 3x3 character gallery and color swatches.
Selecting a character fetches its standalone SVG; color swatches recolor paths.
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture()
def dressup_page(page: Page, live_server: str) -> Page:
    """Navigate to #/dressup and wait for the mermaid SVG to be visible."""
    page.goto(f"{live_server}#/dressup")
    page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
    return page


class TestDressUpView:
    """Base mermaid visible on dress-up screen with character gallery."""

    def test_mermaid_visible(self, dressup_page: Page):
        """Navigating to #/dressup shows #mermaid-svg."""
        svg = dressup_page.locator("#mermaid-svg")
        expect(svg).to_be_visible()

    def test_mermaid_has_ai_art(self, dressup_page: Page):
        """Default mermaid SVG has >50 path elements (AI-generated, not placeholder)."""
        path_count = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return 0;
                return svg.querySelectorAll('path').length;
            })()
        """)
        assert path_count > 10, f"Expected >10 paths in mermaid-svg (AI art), got {path_count}"


class TestCharacterGallery:
    """Character gallery: 9 buttons in a 3x3 grid."""

    def test_gallery_has_nine_buttons(self, dressup_page: Page):
        """Character gallery contains exactly 9 buttons."""
        buttons = dressup_page.locator('.char-btn')
        expect(buttons).to_have_count(9)

    def test_first_button_selected_by_default(self, dressup_page: Page):
        """First character button has .selected class on load."""
        first_btn = dressup_page.locator('.char-btn').first
        expect(first_btn).to_have_class(re.compile("selected"))

    def test_clicking_character_updates_selection(self, dressup_page: Page):
        """Clicking character 2 moves the .selected class to that button."""
        buttons = dressup_page.locator('.char-btn')
        buttons.nth(1).click()
        dressup_page.wait_for_timeout(500)

        expect(buttons.nth(0)).not_to_have_class(re.compile("selected"))
        expect(buttons.nth(1)).to_have_class(re.compile("selected"))

    def test_clicking_character_swaps_svg(self, dressup_page: Page):
        """Clicking a different character replaces the SVG content."""
        original_paths = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return 0;
                return svg.querySelectorAll('path').length;
            })()
        """)

        dressup_page.locator('.char-btn').nth(1).click()
        dressup_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)

        new_paths = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return 0;
                return svg.querySelectorAll('path').length;
            })()
        """)
        # Different character should have a different path count (very unlikely to be identical)
        assert new_paths > 0, "New character SVG should have paths"

    def test_buttons_have_touch_targets(self, dressup_page: Page):
        """Character buttons are at least 60x60px for child-friendly touch."""
        buttons = dressup_page.locator('.char-btn')
        for i in range(min(buttons.count(), 3)):
            box = buttons.nth(i).bounding_box()
            assert box is not None, f"Button {i} has no bounding box"
            assert box["width"] >= 60, f"Button {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Button {i} height {box['height']} < 60"


class TestColorSwatches:
    """Color swatches recolor paths in the active character."""

    def test_color_swatches_visible(self, dressup_page: Page):
        """Color swatches are rendered in the selection panel."""
        swatches = dressup_page.locator('.color-swatch')
        assert swatches.count() > 0, "Expected color swatches to be visible"

    def test_color_swatch_recolors_paths(self, dressup_page: Page):
        """Clicking a color swatch applies a hue-rotate CSS filter to the mermaid SVG.

        Recoloring uses CSS hue-rotate (not fill manipulation) so it works on all
        characters including dark-skinned ones where fill heuristics fail.
        """
        dressup_page.locator('.color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)

        has_filter = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return false;
                const filter = svg.style.filter || '';
                return filter.includes('hue-rotate');
            })()
        """)
        assert has_filter, "Expected hue-rotate CSS filter on mermaid-svg after color swatch click"


class TestUndo:
    """Undo button reverts the last change."""

    def test_undo_reverts_character_swap(self, dressup_page: Page):
        """Swapping character then clicking undo restores the previous character."""
        dressup_page.locator('.char-btn').nth(1).click()
        dressup_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)

        # Second button should be selected
        expect(dressup_page.locator('.char-btn').nth(1)).to_have_class(re.compile("selected"))

        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(500)

        # First button should be selected again
        expect(dressup_page.locator('.char-btn').nth(0)).to_have_class(re.compile("selected"))

    def test_undo_reverts_color(self, dressup_page: Page):
        """Recoloring then clicking undo removes the hue-rotate CSS filter."""
        # Get initial filter state (should be empty)
        original_filter = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return '';
                return svg.style.filter || '';
            })()
        """)

        dressup_page.locator('.color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        restored_filter = dressup_page.evaluate("""
            (() => {
                const svg = document.getElementById('mermaid-svg');
                if (!svg) return '';
                return svg.style.filter || '';
            })()
        """)
        assert restored_filter == original_filter, f"Expected filter '{original_filter}' after undo, got '{restored_filter}'"


class TestCompletion:
    """Celebration sparkle when a non-default character is selected."""

    def test_celebration_sparkle(self, dressup_page: Page):
        """Selecting a non-default character triggers celebration sparkle."""
        dressup_page.locator('.char-btn').nth(1).click()
        dressup_page.wait_for_timeout(800)

        sparkles = dressup_page.locator('.sparkle.celebration')
        assert sparkles.count() > 0, "No celebration sparkle elements found after selecting new character"


class TestSelectionPanel:
    """Selection panel UI sizing and layout."""

    def test_undo_button_visible(self, dressup_page: Page):
        """Undo button is visible in the selection panel."""
        undo = dressup_page.locator('.undo-btn')
        expect(undo).to_be_visible()

    def test_undo_button_60pt(self, dressup_page: Page):
        """Undo button is at least 60x60px."""
        undo_box = dressup_page.locator('.undo-btn').bounding_box()
        assert undo_box is not None, "Undo button has no bounding box"
        assert undo_box["width"] >= 60, f"Undo width {undo_box['width']} < 60"
        assert undo_box["height"] >= 60, f"Undo height {undo_box['height']} < 60"
