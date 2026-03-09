"""Tests for FastAPI static file serving."""


def test_root_returns_html(client):
    """GET / returns 200 with HTML content-type."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_css_returns_css(client):
    """GET /css/style.css returns 200 with CSS content-type."""
    response = client.get("/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_nonexistent_returns_404(client):
    """GET /nonexistent returns 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_static_only_no_cors_needed(client):
    """Static-only app has no CORS configuration needed."""
    response = client.get("/")
    # No CORS headers should be present since this is a static-only app
    assert "access-control-allow-origin" not in response.headers
