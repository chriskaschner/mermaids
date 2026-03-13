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
