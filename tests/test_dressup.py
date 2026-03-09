"""End-to-end Playwright tests for dress-up requirements (DRSS-01 through DRSS-07).

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
All tests exercise the UI buttons in the selection panel, not JS functions directly.
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
    """DRSS-01: Base mermaid visible on dress-up screen with default parts."""

    def test_mermaid_visible(self, dressup_page: Page):
        """Navigating to #/dressup shows #mermaid-svg with at least 3 data-region elements."""
        svg = dressup_page.locator("#mermaid-svg")
        expect(svg).to_be_visible()
        regions = dressup_page.locator("[data-region]")
        assert regions.count() >= 3, f"Expected >= 3 data-region elements, got {regions.count()}"

    def test_base_mermaid_has_default_parts(self, dressup_page: Page):
        """Default parts: active-tail href=#tail-1, active-hair href=#hair-1, active-acc href=#acc-none."""
        tail_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert tail_href == "#tail-1", f"Expected #tail-1, got {tail_href}"

        hair_href = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert hair_href == "#hair-1", f"Expected #hair-1, got {hair_href}"

        acc_href = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert acc_href == "#acc-none", f"Expected #acc-none, got {acc_href}"


class TestPartSwapping:
    """DRSS-02, DRSS-03, DRSS-04: Swapping tails, hair, and accessories."""

    def test_tail_swap(self, dressup_page: Page):
        """Clicking a tail option button changes #active-tail href to the selected variant."""
        # Click the tail category tab
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        # Click the second tail option (tail-2)
        options = dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]')
        options.click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert href == "#tail-2", f"Expected #tail-2, got {href}"

    def test_hair_swap(self, dressup_page: Page):
        """Clicking a hair option button changes #active-hair href to the selected variant."""
        # Click the hair category tab
        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        # Click the second hair option (hair-2)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert href == "#hair-2", f"Expected #hair-2, got {href}"

    def test_accessory_swap(self, dressup_page: Page):
        """Clicking an accessory option button changes #active-acc href to the selected variant."""
        # Click the accessory category tab
        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        # Click the crown accessory (acc-1)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-1"]').click()
        dressup_page.wait_for_timeout(200)
        href = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert href == "#acc-1", f"Expected #acc-1, got {href}"

    def test_all_categories_have_options(self, dressup_page: Page):
        """Tail has 3 options, hair has 3 options, accessory has 4 options (including 'none')."""
        # Check tail options
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        tail_opts = dressup_page.locator('.options-row .option-btn')
        assert tail_opts.count() == 3, f"Expected 3 tail options, got {tail_opts.count()}"

        # Check hair options
        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        hair_opts = dressup_page.locator('.options-row .option-btn')
        assert hair_opts.count() == 3, f"Expected 3 hair options, got {hair_opts.count()}"

        # Check accessory options
        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        acc_opts = dressup_page.locator('.options-row .option-btn')
        assert acc_opts.count() == 4, f"Expected 4 accessory options, got {acc_opts.count()}"


class TestColorRecolor:
    """DRSS-05: Clicking a color swatch changes the fill on active variant elements."""

    def test_color_swatch_changes_fill(self, dressup_page: Page):
        """Clicking a color swatch changes the fill attribute on elements within the active variant's source group in defs."""
        # Select the tail category
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        # Switch to color tab
        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(200)
        # Click a color swatch (hot pink)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)
        # Verify the fill changed on the active tail variant source in defs
        fill = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return null;
                const filled = source.querySelector('path[fill]:not([fill="none"])');
                return filled ? filled.getAttribute('fill') : null;
            })()
        """)
        assert fill == "#ff69b4", f"Expected fill #ff69b4, got {fill}"


class TestUndo:
    """DRSS-06: Undo button reverts the last change."""

    def test_undo_reverts_swap(self, dressup_page: Page):
        """Swapping a part then clicking undo restores the previous href."""
        # Verify initial tail
        initial_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert initial_href == "#tail-1"

        # Swap to tail-2
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        swapped_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert swapped_href == "#tail-2"

        # Click undo
        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        restored_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert restored_href == "#tail-1", f"Expected #tail-1 after undo, got {restored_href}"

    def test_undo_reverts_color(self, dressup_page: Page):
        """Recoloring then clicking undo restores the previous fill."""
        # Get original fill on tail-1
        original_fill = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return null;
                const filled = source.querySelector('path[fill]:not([fill="none"])');
                return filled ? filled.getAttribute('fill') : null;
            })()
        """)

        # Select tail category, then color tab, then apply pink
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)

        # Verify color changed
        changed_fill = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return null;
                const filled = source.querySelector('path[fill]:not([fill="none"])');
                return filled ? filled.getAttribute('fill') : null;
            })()
        """)
        assert changed_fill == "#ff69b4"

        # Click undo
        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        # Verify color restored
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
    """DRSS-07: Celebration sparkle when all parts have non-default selections."""

    def test_celebration_sparkle(self, dressup_page: Page):
        """Selecting non-default tail, hair, AND accessory triggers .sparkle.celebration elements."""
        # Swap tail to tail-2
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        # Swap hair to hair-2
        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)

        # Swap accessory to acc-1 (this should trigger completion)
        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-1"]').click()
        dressup_page.wait_for_timeout(500)

        # Check for celebration sparkle elements
        sparkles = dressup_page.locator('.sparkle.celebration')
        assert sparkles.count() > 0, "No celebration sparkle elements found after completing all parts"


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
        # Check category tabs
        tabs = dressup_page.locator('.cat-tab')
        for i in range(tabs.count()):
            box = tabs.nth(i).bounding_box()
            assert box is not None, f"Tab {i} has no bounding box"
            assert box["width"] >= 60, f"Tab {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Tab {i} height {box['height']} < 60"

        # Check undo button
        undo_box = dressup_page.locator('.undo-btn').bounding_box()
        assert undo_box is not None, "Undo button has no bounding box"
        assert undo_box["width"] >= 60, f"Undo width {undo_box['width']} < 60"
        assert undo_box["height"] >= 60, f"Undo height {undo_box['height']} < 60"

        # Check option buttons in the active category
        options = dressup_page.locator('.options-row .option-btn')
        for i in range(options.count()):
            box = options.nth(i).bounding_box()
            assert box is not None, f"Option {i} has no bounding box"
            assert box["width"] >= 60, f"Option {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Option {i} height {box['height']} < 60"
