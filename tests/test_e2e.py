"""End-to-end Playwright tests for routing, navigation, touch interaction, and sparkle effects.

Tests run with iPad emulation (1024x1366, touch, WebKit) via conftest.py fixtures.
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture()
def app_page(page: Page, live_server: str) -> Page:
    """Navigate to the app and wait for it to be ready."""
    page.goto(live_server)
    page.wait_for_selector("#app", state="attached")
    # Allow router to settle
    page.wait_for_timeout(300)
    return page


class TestHomeView:
    """Home view loads and displays activity buttons."""

    def test_home_view_loads(self, app_page: Page):
        """App loads and displays home view with activity buttons."""
        expect(app_page.locator("#app")).to_be_visible()
        buttons = app_page.locator(".activity-btn")
        expect(buttons).to_have_count(2)

    def test_home_activity_buttons_size(self, app_page: Page):
        """Each activity button is at least 60x60 px (FOUN-01 tap target)."""
        buttons = app_page.locator(".activity-btn")
        count = buttons.count()
        assert count == 2, f"Expected 2 activity buttons, got {count}"
        for i in range(count):
            box = buttons.nth(i).bounding_box()
            assert box is not None, f"Button {i} has no bounding box"
            assert box["width"] >= 60, f"Button {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Button {i} height {box['height']} < 60"


class TestNavigation:
    """Hash-based routing and navigation."""

    def test_navigate_to_dressup(self, app_page: Page):
        """Tapping dress-up button navigates to /#/dressup."""
        app_page.locator(".activity-btn").first.click()
        app_page.wait_for_timeout(300)
        assert "dressup" in app_page.url

    def test_navigate_to_coloring(self, app_page: Page):
        """Tapping coloring button navigates to /#/coloring."""
        app_page.locator(".activity-btn").nth(1).click()
        app_page.wait_for_timeout(300)
        assert "coloring" in app_page.url

    def test_dressup_shows_mermaid_svg(self, app_page: Page):
        """Dress-up view displays the mermaid SVG and character gallery."""
        app_page.goto(app_page.url.split("#")[0] + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        svg = app_page.locator("#mermaid-svg")
        expect(svg).to_be_visible()
        gallery = app_page.locator(".character-gallery .char-btn")
        assert gallery.count() == 9, f"Expected 9 character buttons, got {gallery.count()}"

    def test_nav_visible_on_all_views(self, app_page: Page):
        """Navigation bar is visible on every view."""
        base = app_page.url.split("#")[0]
        for route in ["#/home", "#/dressup", "#/coloring"]:
            app_page.goto(base + route)
            app_page.wait_for_timeout(300)
            nav = app_page.locator("#nav-bar")
            expect(nav).to_be_visible()

    def test_nav_switching(self, app_page: Page):
        """From dress-up, tapping coloring nav icon switches view."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_timeout(300)
        # Tap coloring nav icon
        app_page.locator('.nav-icon[data-view="coloring"]').click()
        app_page.wait_for_timeout(300)
        assert "coloring" in app_page.url


class TestTouchInteraction:
    """SVG touch events and sparkle particle effects."""

    def test_character_select_triggers_celebration_sparkle(self, app_page: Page):
        """Selecting a non-default character triggers celebration sparkle."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        # Select second character to trigger celebration
        app_page.locator(".char-btn").nth(1).click()
        app_page.wait_for_timeout(800)
        sparkles = app_page.locator(".sparkle.celebration")
        assert sparkles.count() > 0, "No celebration sparkle elements found after character select"

    def test_celebration_sparkle_cleanup(self, app_page: Page):
        """Celebration sparkle elements are removed from DOM after animation."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        app_page.locator(".char-btn").nth(1).click()
        app_page.wait_for_timeout(800)
        assert app_page.locator(".sparkle.celebration").count() > 0
        # Wait for cleanup (1s celebration animation + buffer)
        app_page.wait_for_timeout(1500)
        assert app_page.locator(".sparkle.celebration").count() == 0, "Sparkles not cleaned up"


class TestTapTargets:
    """All interactive elements meet minimum size requirements."""

    def test_tap_targets_minimum_size(self, app_page: Page):
        """All data-region and nav-icon elements are at least 60x60."""
        base = app_page.url.split("#")[0]
        # Check nav icons (visible on all views)
        nav_icons = app_page.locator(".nav-icon")
        for i in range(nav_icons.count()):
            box = nav_icons.nth(i).bounding_box()
            assert box is not None, f"Nav icon {i} has no bounding box"
            assert box["width"] >= 60, f"Nav icon {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Nav icon {i} height {box['height']} < 60"

        # Check data-region elements in dress-up view
        app_page.goto(base + "#/dressup")
        app_page.wait_for_timeout(500)
        regions = app_page.locator("[data-region]")
        for i in range(regions.count()):
            box = regions.nth(i).bounding_box()
            assert box is not None, f"Region {i} has no bounding box"
            assert box["width"] >= 60, f"Region {i} width {box['width']} < 60"
            assert box["height"] >= 60, f"Region {i} height {box['height']} < 60"


class TestIconSemantics:
    """Nav bar and home screen icons have correct semantic attributes (ICON-01)."""

    def test_nav_icons_have_aria_labels(self, app_page: Page):
        """Each .nav-icon element has a non-empty aria-label attribute."""
        nav_icons = app_page.locator(".nav-icon")
        count = nav_icons.count()
        assert count > 0, "No .nav-icon elements found"
        for i in range(count):
            label = nav_icons.nth(i).get_attribute("aria-label")
            assert label, f"Nav icon {i} has missing or empty aria-label (got {label!r})"

    def test_nav_icon_labels_are_distinct(self, app_page: Page):
        """All .nav-icon aria-labels are unique — no duplicates."""
        nav_icons = app_page.locator(".nav-icon")
        labels = [nav_icons.nth(i).get_attribute("aria-label") for i in range(nav_icons.count())]
        assert len(labels) == len(set(labels)), (
            f"Nav icon aria-labels are not all distinct: {labels}"
        )

    def test_nav_icons_contain_svg(self, app_page: Page):
        """Each .nav-icon contains at least one <svg> child element."""
        nav_icons = app_page.locator(".nav-icon")
        count = nav_icons.count()
        assert count > 0, "No .nav-icon elements found"
        for i in range(count):
            svg_count = nav_icons.nth(i).locator("svg").count()
            assert svg_count >= 1, (
                f"Nav icon {i} (aria-label={nav_icons.nth(i).get_attribute('aria-label')!r}) "
                f"contains no <svg> child"
            )

    def test_activity_buttons_have_svg_and_labels(self, app_page: Page):
        """Each .activity-btn on the home view has a non-empty aria-label and an <svg> child."""
        expected_labels = {"Dress Up", "Coloring"}
        buttons = app_page.locator(".activity-btn")
        count = buttons.count()
        assert count == 2, f"Expected 2 .activity-btn elements, got {count}"
        found_labels = set()
        for i in range(count):
            label = buttons.nth(i).get_attribute("aria-label")
            assert label, f"Activity button {i} has missing or empty aria-label (got {label!r})"
            found_labels.add(label)
            svg_count = buttons.nth(i).locator("svg").count()
            assert svg_count >= 1, (
                f"Activity button {i} (aria-label={label!r}) contains no <svg> child"
            )
        assert found_labels == expected_labels, (
            f"Activity button labels {found_labels!r} != expected {expected_labels!r}"
        )


class TestDressUpToColoring:
    """Dress-up → coloring pipeline: 'Color This!' button and routing."""

    def test_color_this_button_visible(self, app_page: Page):
        """'Color This!' button is visible in the dress-up view."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        btn = app_page.locator(".color-this-btn")
        expect(btn).to_be_visible()
        assert "Color This" in btn.inner_text(), (
            f"Button text does not contain 'Color This': {btn.inner_text()!r}"
        )

    def test_color_this_navigates_to_coloring_canvas(self, app_page: Page):
        """Clicking 'Color This!' with default character navigates to the coloring canvas."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        # Click the button
        app_page.locator(".color-this-btn").click()
        # Wait for canvas to appear
        app_page.wait_for_selector("#coloring-canvas", state="attached", timeout=8000)
        # Verify canvas is present
        canvas = app_page.locator("#coloring-canvas")
        expect(canvas).to_be_visible()
        # Verify coloring view container
        coloring_view = app_page.locator(".coloring-view")
        expect(coloring_view).to_be_visible()
        # Verify URL contains the default character
        assert "character=mermaid-1" in app_page.url, (
            f"URL does not contain 'character=mermaid-1': {app_page.url}"
        )

    def test_color_this_with_different_character(self, app_page: Page):
        """After selecting mermaid-3, 'Color This!' routes to mermaid-3's outline."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        # Select the 3rd character button (index 2 → mermaid-3)
        app_page.locator(".char-btn").nth(2).click()
        app_page.wait_for_timeout(400)  # allow SVG swap + state update
        # Click Color This!
        app_page.locator(".color-this-btn").click()
        app_page.wait_for_selector("#coloring-canvas", state="attached", timeout=8000)
        # Verify URL contains mermaid-3
        assert "character=mermaid-3" in app_page.url, (
            f"URL does not contain 'character=mermaid-3': {app_page.url}"
        )

    def test_color_this_back_button_returns_to_dressup(self, app_page: Page):
        """Back button in character coloring view returns to dress-up (not gallery)."""
        base = app_page.url.split("#")[0]
        app_page.goto(base + "#/dressup")
        app_page.wait_for_selector("#mermaid-svg", state="visible", timeout=5000)
        app_page.locator(".color-this-btn").click()
        app_page.wait_for_selector("#coloring-canvas", state="attached", timeout=8000)
        # Click back
        app_page.locator(".back-btn").click()
        app_page.wait_for_timeout(500)
        # Should be on dressup, not coloring gallery
        assert "dressup" in app_page.url, (
            f"Expected URL to contain 'dressup' after back, got: {app_page.url}"
        )
        expect(app_page.locator("#mermaid-svg")).to_be_visible()
