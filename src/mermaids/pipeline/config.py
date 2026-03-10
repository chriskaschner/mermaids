"""Shared constants for the art generation pipeline.

Paths, retry configuration, and image sizes used by both coloring
page and dress-up generation workflows.
"""

from pathlib import Path

# Project root: three parents up from this file
# (src/mermaids/pipeline/config.py -> src/mermaids/pipeline -> src/mermaids -> src -> root)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent

# Generated intermediate artifacts (not served to frontend)
GENERATED_PNG_DIR: Path = PROJECT_ROOT / "assets" / "generated" / "png"
GENERATED_SVG_DIR: Path = PROJECT_ROOT / "assets" / "generated" / "svg"

# Final SVG assets served by the frontend
FRONTEND_SVG_DIR: Path = PROJECT_ROOT / "frontend" / "assets" / "svg"

# Retry settings for OpenAI API calls
RETRY_MAX: int = 3
RETRY_BASE_DELAY: float = 2.0

# Default image generation size
IMAGE_SIZE: str = "1024x1024"
