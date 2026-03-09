"""FastAPI application with static file serving for the Mermaid Create & Play frontend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API routes go here (none needed for Phase 1)
# @app.get("/api/...")

# Mount frontend last -- catches all non-API routes
_frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
