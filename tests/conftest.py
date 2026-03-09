"""Shared test fixtures for FastAPI and Playwright."""

import socket
import threading

import pytest
import uvicorn
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from mermaids.app import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient for synchronous API tests."""
    return TestClient(app)


def _get_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """Start a uvicorn server in a background thread for E2E tests.

    Returns the base URL (e.g., http://127.0.0.1:PORT).
    """
    port = _get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    import time
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure iPad emulation for all Playwright tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1024, "height": 1366},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": (
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        ),
    }
