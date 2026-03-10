"""End-to-end Playwright tests for dress-up character selection.

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
All tests exercise the UI buttons in the selection panel, not JS functions directly.

The dress-up uses a single <use id="active-character"> that swaps between
complete AI-generated character variants organized by category (tail/hair/acc).
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture()
def dressup_page(page: Page, live_server: str) -> Page:
    """Navigate to #/dressup and wait for the mermaid SVG to be visible."""
    page.goto(f"{live_server}#/dressup")
    page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
    return page


class TestDressUpView:
    """Base mermaid visible on dress-up screen with default character."""

    def test_mermaid_visible(self, dressup_page: Page):
        """Navigating to #/dressup shows #mermaid-svg with the active character."""
        svg = dressup_page.locator("#mermaid-svg")
        expect(svg).to_be_visible()
        character = dressup_page.locator("#active-character")
        assert character.count() == 1, "Expected single #active-character use element"

    def test_mermaid_has_ai_art(self, dressup_page: Page):
        """Variant defs groups contain >50 path elements (AI-generated, not hand-crafted)."""
        path_count = dressup_page.evaluate("""
            (() => {
                const group = document.getElementById('tail-1');
                if (!group) return 0;
                return group.querySelectorAll('path').length;
            })()
        """)
        assert path_count > 50, f"Expected >50 paths in tail-1 (AI art), got {path_count}"

    def test_default_character(self, dressup_page: Page):
        """Default character: active-character href=#tail-1."""
        href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert href == "#tail-1", f"Expected #tail-1, got {href}"


class TestPartSwapping:
    """Swapping characters via category tabs."""

    def test_tail_swap(self, dressup_page: Page):
        """Clicking a tail option changes #active-character href."""
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert href == "#tail-2", f"Expected #tail-2, got {href}"

    def test_hair_swap(self, dressup_page: Page):
        """Clicking a hair option changes #active-character href."""
        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert href == "#hair-2", f"Expected #hair-2, got {href}"

    def test_accessory_swap(self, dressup_page: Page):
        """Clicking an accessory option changes #active-character href."""
        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-1"]').click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert href == "#acc-1", f"Expected #acc-1, got {href}"

    def test_all_categories_have_options(self, dressup_page: Page):
        """Each category has 3 character options."""
        for cat, expected in [("tail", 3), ("hair", 3), ("acc", 3)]:
            dressup_page.locator(f'.cat-tab[data-category="{cat}"]').click()
            dressup_page.wait_for_timeout(200)
            opts = dressup_page.locator('.options-row .option-btn')
            assert opts.count() == expected, f"Expected {expected} {cat} options, got {opts.count()}"


class TestColorRecolor:
    """Clicking a color swatch recolors the active character."""

    def test_color_swatch_changes_fill(self, dressup_page: Page):
        """Clicking a color swatch changes fill on recolorable elements in the active character."""
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)
        has_pink = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return false;
                const paths = source.querySelectorAll('path');
                return Array.from(paths).some(p => p.getAttribute('fill') === '#ff69b4');
            })()
        """)
        assert has_pink, "Expected at least one path with fill #ff69b4 after recolor"


class TestUndo:
    """Undo button reverts the last change."""

    def test_undo_reverts_swap(self, dressup_page: Page):
        """Swapping a character then clicking undo restores the previous href."""
        initial_href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert initial_href == "#tail-1"

        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        swapped_href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert swapped_href == "#tail-2"

        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        restored_href = dressup_page.evaluate(
            "document.getElementById('active-character')?.getAttribute('href')"
        )
        assert restored_href == "#tail-1", f"Expected #tail-1 after undo, got {restored_href}"

    def test_undo_reverts_color(self, dressup_page: Page):
        """Recoloring then clicking undo restores the previous fill."""
        original_fill = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return null;
                const filled = source.querySelector('path[fill]:not([fill="none"])');
                return filled ? filled.getAttribute('fill') : null;
            })()
        """)

        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        restored_fill = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return null;
                const filled = source.querySelector('path[fill]:not([fill="none"])');
                return filled ? filled.getAttribute('fill') : null;
            })()
        """)
        assert restored_fill == original_fill, f"Expected {original_fill} after undo, got {restored_fill}"


class TestCompletion:
    """Celebration sparkle when all categories have non-default selections."""

    def test_celebration_sparkle(self, dressup_page: Page):
        """Selecting non-default in all 3 categories triggers celebration."""
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-2"]').click()
        dressup_page.wait_for_timeout(500)

        sparkles = dressup_page.locator('.sparkle.celebration')
        assert sparkles.count() > 0, "No celebration sparkle elements found after completing all categories"


class TestSelectionPanel:
    """Selection panel UI: category tabs, option buttons, and sizing."""

    def test_category_tabs_visible(self, dressup_page: Page):
        """4 category tab buttons (tail, hair, acc, color) and 1 undo button are visible."""
        tabs = dressup_page.locator('.cat-tab')
        expect(tabs).to_have_count(4)
        for i in range(4):
            expect(tabs.nth(i)).to_be_visible()

        undo = dressup_page.locator('.undo-btn')
        expect(undo).to_be_visible()

    def test_option_buttons_60pt(self, dressup_page: Page):
        """All option buttons and category tabs are at least 60x60px."""
        tabs = dressup_page.locator('.cat-tab')
        for i in range(tabs.count()):
            box = tabs.nth(i).bounding_box()
            assert box is not None, f"Tab {i} has no bounding box"
            assert box["width"] >= 60, f"Tab {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Tab {i} height {box['height']} < 60"

        undo_box = dressup_page.locator('.undo-btn').bounding_box()
        assert undo_box is not None, "Undo button has no bounding box"
        assert undo_box["width"] >= 60, f"Undo width {undo_box['width']} < 60"
        assert undo_box["height"] >= 60, f"Undo height {undo_box['height']} < 60"

        options = dressup_page.locator('.options-row .option-btn')
        for i in range(options.count()):
            box = options.nth(i).bounding_box()
            assert box is not None, f"Option {i} has no bounding box"
            assert box["width"] >= 60, f"Option {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Option {i} height {box['height']} < 60"


class TestPreviewThumbnails:
    """Preview thumbnails show actual traced SVGs fetched at runtime."""

    def test_preview_contains_svg(self, dressup_page: Page):
        """Option buttons contain an SVG element with viewBox."""
        dressup_page.wait_for_selector(".option-btn svg", timeout=5000)
        has_svg = dressup_page.evaluate("""
            (() => {
                const btn = document.querySelector('.option-btn');
                if (!btn) return false;
                const svg = btn.querySelector('svg');
                return svg !== null && svg.hasAttribute('viewBox');
            })()
        """)
        assert has_svg, "Expected .option-btn to contain an SVG element with viewBox"

    def test_preview_svg_is_48x48(self, dressup_page: Page):
        """SVG inside option buttons has width=48 and height=48."""
        dressup_page.wait_for_selector(".option-btn svg", timeout=5000)
        dims = dressup_page.evaluate("""
            (() => {
                const btn = document.querySelector('.option-btn');
                if (!btn) return null;
                const svg = btn.querySelector('svg');
                if (!svg) return null;
                return {
                    width: svg.getAttribute('width'),
                    height: svg.getAttribute('height')
                };
            })()
        """)
        assert dims is not None, "No SVG found in option button"
        assert dims["width"] == "48", f"Expected width=48, got {dims['width']}"
        assert dims["height"] == "48", f"Expected height=48, got {dims['height']}"

    def test_preview_fetched_not_inline(self, dressup_page: Page):
        """Option button SVG has >10 path elements (fetched traced SVG, not inline icon)."""
        dressup_page.wait_for_selector(".option-btn svg", timeout=5000)
        path_count = dressup_page.evaluate("""
            (() => {
                const btn = document.querySelector('.option-btn');
                if (!btn) return 0;
                const svg = btn.querySelector('svg');
                if (!svg) return 0;
                return svg.querySelectorAll('path').length;
            })()
        """)
        assert path_count > 10, f"Expected >10 paths in preview SVG (fetched art), got {path_count}"


class TestPreviewColorSync:
    """Preview thumbnails reflect applied color overrides."""

    def test_preview_reflects_color_after_recolor(self, dressup_page: Page):
        """After recoloring, switching tabs and back shows recolored preview."""
        dressup_page.wait_for_selector(".option-btn svg", timeout=5000)

        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(300)

        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(300)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(300)

        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(500)

        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_selector(".option-btn svg", timeout=5000)
        dressup_page.wait_for_timeout(500)

        has_pink = dressup_page.evaluate("""
            (() => {
                const btn = document.querySelector('.option-btn[data-variant="tail-1"]');
                if (!btn) return false;
                const svg = btn.querySelector('svg');
                if (!svg) return false;
                const paths = svg.querySelectorAll('path');
                return Array.from(paths).some(p => p.getAttribute('fill') === '#ff69b4');
            })()
        """)
        assert has_pink, "Expected preview to reflect #ff69b4 color after recolor"
