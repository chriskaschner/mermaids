"""End-to-end Playwright tests for dress-up character selection.

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
All tests exercise the UI buttons in the selection panel, not JS functions directly.

The dress-up uses stacked <use> elements (active-tail, active-body, active-hair,
active-eyes, active-acc) that each swap independently via href changes.
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
    """Base mermaid visible on dress-up screen with multi-layer use structure."""

    def test_mermaid_visible(self, dressup_page: Page):
        """Navigating to #/dressup shows #mermaid-svg with active layer use elements."""
        svg = dressup_page.locator("#mermaid-svg")
        expect(svg).to_be_visible()
        # New multi-use structure: each layer has its own use element
        hair_use = dressup_page.locator("#active-hair")
        assert hair_use.count() == 1, "Expected #active-hair use element"
        eyes_use = dressup_page.locator("#active-eyes")
        assert eyes_use.count() == 1, "Expected #active-eyes use element"
        tail_use = dressup_page.locator("#active-tail")
        assert tail_use.count() == 1, "Expected #active-tail use element"
        acc_use = dressup_page.locator("#active-acc")
        assert acc_use.count() == 1, "Expected #active-acc use element"

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

    def test_default_layers(self, dressup_page: Page):
        """Default state: each layer references its variant-1 part."""
        hair_href = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert hair_href == "#hair-1", f"Expected #hair-1, got {hair_href}"

        tail_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert tail_href == "#tail-1", f"Expected #tail-1, got {tail_href}"

        eyes_href = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        assert eyes_href == "#eye-1", f"Expected #eye-1, got {eyes_href}"

        acc_href = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert acc_href == "#acc-1", f"Expected #acc-1, got {acc_href}"


class TestPartSwapping:
    """Swapping parts via category tabs -- each swap changes only the target layer."""

    def test_hair_swap_only_changes_hair(self, dressup_page: Page):
        """Clicking hair-2 changes only active-hair href; tail, eyes, acc stay unchanged."""
        # Record current state of other layers
        tail_before = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        eyes_before = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        acc_before = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )

        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)

        hair_href = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert hair_href == "#hair-2", f"Expected #hair-2, got {hair_href}"

        # Other layers must be unchanged
        tail_after = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        eyes_after = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        acc_after = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert tail_after == tail_before, f"Expected tail unchanged ({tail_before}), got {tail_after}"
        assert eyes_after == eyes_before, f"Expected eyes unchanged ({eyes_before}), got {eyes_after}"
        assert acc_after == acc_before, f"Expected acc unchanged ({acc_before}), got {acc_after}"

    def test_tail_swap_only_changes_tail(self, dressup_page: Page):
        """Clicking tail-2 changes only active-tail href; hair, eyes, acc stay unchanged."""
        hair_before = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        eyes_before = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        acc_before = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )

        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        tail_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert tail_href == "#tail-2", f"Expected #tail-2, got {tail_href}"

        hair_after = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        eyes_after = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        acc_after = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert hair_after == hair_before, f"Expected hair unchanged, got {hair_after}"
        assert eyes_after == eyes_before, f"Expected eyes unchanged, got {eyes_after}"
        assert acc_after == acc_before, f"Expected acc unchanged, got {acc_after}"

    def test_accessory_swap_only_changes_acc(self, dressup_page: Page):
        """Clicking acc-2 changes only active-acc href; hair, eyes, tail stay unchanged."""
        hair_before = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        eyes_before = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        tail_before = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )

        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-2"]').click()
        dressup_page.wait_for_timeout(200)

        acc_href = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert acc_href == "#acc-2", f"Expected #acc-2, got {acc_href}"

        hair_after = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        eyes_after = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        tail_after = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert hair_after == hair_before, f"Expected hair unchanged, got {hair_after}"
        assert eyes_after == eyes_before, f"Expected eyes unchanged, got {eyes_after}"
        assert tail_after == tail_before, f"Expected tail unchanged, got {tail_after}"

    def test_all_categories_have_options(self, dressup_page: Page):
        """Each of the 4 part categories has 3 option buttons."""
        for cat, expected in [("hair", 3), ("eyes", 3), ("tail", 3), ("acc", 3)]:
            dressup_page.locator(f'.cat-tab[data-category="{cat}"]').click()
            dressup_page.wait_for_timeout(200)
            opts = dressup_page.locator('.options-row .option-btn')
            assert opts.count() == expected, f"Expected {expected} {cat} options, got {opts.count()}"


class TestEyeCategory:
    """Eyes tab and eye swapping -- new category in v1.2."""

    def test_eye_tab_visible(self, dressup_page: Page):
        """Eyes tab with data-category='eyes' exists and is visible."""
        tab = dressup_page.locator('.cat-tab[data-category="eyes"]')
        assert tab.count() == 1, "Expected exactly one eyes tab"
        expect(tab).to_be_visible()

    def test_eye_swap_only_changes_eyes(self, dressup_page: Page):
        """Clicking eye-2 changes only active-eyes href; hair, tail, acc stay unchanged."""
        hair_before = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        tail_before = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        acc_before = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )

        dressup_page.locator('.cat-tab[data-category="eyes"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="eye-2"]').click()
        dressup_page.wait_for_timeout(200)

        eyes_href = dressup_page.evaluate(
            "document.getElementById('active-eyes')?.getAttribute('href')"
        )
        assert eyes_href == "#eye-2", f"Expected #eye-2, got {eyes_href}"

        hair_after = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        tail_after = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        acc_after = dressup_page.evaluate(
            "document.getElementById('active-acc')?.getAttribute('href')"
        )
        assert hair_after == hair_before, f"Expected hair unchanged, got {hair_after}"
        assert tail_after == tail_before, f"Expected tail unchanged, got {tail_after}"
        assert acc_after == acc_before, f"Expected acc unchanged, got {acc_after}"

    def test_eye_options_count(self, dressup_page: Page):
        """Eyes tab shows 3 option buttons (eye-1, eye-2, eye-3)."""
        dressup_page.locator('.cat-tab[data-category="eyes"]').click()
        dressup_page.wait_for_timeout(200)
        opts = dressup_page.locator('.options-row .option-btn')
        assert opts.count() == 3, f"Expected 3 eye options, got {opts.count()}"
        for variant in ["eye-1", "eye-2", "eye-3"]:
            btn = dressup_page.locator(f'.options-row .option-btn[data-variant="{variant}"]')
            assert btn.count() == 1, f"Expected button for {variant}"


class TestColorRecolor:
    """Clicking a color swatch recolors only the active category's part."""

    def test_color_swatch_changes_fill_active_part(self, dressup_page: Page):
        """Color swatch recolors the active category's source group, not other parts."""
        # Activate eyes category, then open color tab
        dressup_page.locator('.cat-tab[data-category="eyes"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.cat-tab[data-category="color"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .color-swatch[data-color="#ff69b4"]').click()
        dressup_page.wait_for_timeout(200)

        # The current eye variant (eye-1) should have pink
        has_pink_eyes = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('eye-1');
                if (!source) return false;
                const els = source.querySelectorAll('path, circle, ellipse, rect');
                return Array.from(els).some(el => el.getAttribute('fill') === '#ff69b4');
            })()
        """)
        assert has_pink_eyes, "Expected at least one element with fill #ff69b4 in eye-1 after recolor"

        # tail-1 should NOT have been recolored
        has_pink_tail = dressup_page.evaluate("""
            (() => {
                const source = document.getElementById('tail-1');
                if (!source) return false;
                const els = source.querySelectorAll('path, circle, ellipse, rect');
                return Array.from(els).some(el => el.getAttribute('fill') === '#ff69b4');
            })()
        """)
        assert not has_pink_tail, "tail-1 should NOT be recolored when eyes is the active category"

    def test_color_swatch_changes_tail_when_tail_active(self, dressup_page: Page):
        """Color swatch recolors tail-1 when tail is active category."""
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
        assert has_pink, "Expected at least one path with fill #ff69b4 in tail-1 after recolor"


class TestUndo:
    """Undo button reverts the last change."""

    def test_undo_reverts_swap(self, dressup_page: Page):
        """Swapping a part then clicking undo restores only that category's previous href."""
        initial_hair = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert initial_hair == "#hair-1", f"Expected initial #hair-1, got {initial_hair}"

        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)

        swapped = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert swapped == "#hair-2", f"Expected #hair-2 after swap, got {swapped}"

        dressup_page.locator('.undo-btn').click()
        dressup_page.wait_for_timeout(200)

        restored = dressup_page.evaluate(
            "document.getElementById('active-hair')?.getAttribute('href')"
        )
        assert restored == "#hair-1", f"Expected #hair-1 after undo, got {restored}"

        # Other categories should be unaffected
        tail_href = dressup_page.evaluate(
            "document.getElementById('active-tail')?.getAttribute('href')"
        )
        assert tail_href == "#tail-1", f"Expected tail unchanged at #tail-1, got {tail_href}"

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
    """Celebration sparkle when all 4 categories have non-default selections."""

    def test_celebration_sparkle(self, dressup_page: Page):
        """Selecting non-default in all 4 categories triggers celebration."""
        dressup_page.locator('.cat-tab[data-category="tail"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="tail-2"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.cat-tab[data-category="hair"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="hair-2"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.cat-tab[data-category="eyes"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="eye-2"]').click()
        dressup_page.wait_for_timeout(200)

        dressup_page.locator('.cat-tab[data-category="acc"]').click()
        dressup_page.wait_for_timeout(200)
        dressup_page.locator('.options-row .option-btn[data-variant="acc-2"]').click()
        dressup_page.wait_for_timeout(500)

        sparkles = dressup_page.locator('.sparkle.celebration')
        assert sparkles.count() > 0, "No celebration sparkle elements found after completing all 4 categories"


class TestSelectionPanel:
    """Selection panel UI: category tabs, option buttons, and sizing."""

    def test_category_tabs_visible(self, dressup_page: Page):
        """5 category tab buttons (hair, eyes, tail, acc, color) and 1 undo button are visible."""
        tabs = dressup_page.locator('.cat-tab')
        expect(tabs).to_have_count(5)
        for i in range(5):
            expect(tabs.nth(i)).to_be_visible()

        undo = dressup_page.locator('.undo-btn')
        expect(undo).to_be_visible()

    def test_hair_tab_is_default_active(self, dressup_page: Page):
        """Hair tab is active (highlighted) by default on load."""
        hair_tab = dressup_page.locator('.cat-tab[data-category="hair"]')
        expect(hair_tab).to_have_class("cat-tab active")

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
