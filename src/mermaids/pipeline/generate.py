"""OpenAI image generation with retry and idempotent skip.

Provides generate_image() for single image generation and
generate_coloring_pages() for batch coloring page creation.
"""

import base64
import time
from pathlib import Path

import openai

from mermaids.pipeline.config import (
    GENERATED_PNG_DIR,
    IMAGE_SIZE,
    RETRY_BASE_DELAY,
    RETRY_MAX,
)
from mermaids.pipeline.prompts import COLORING_BASE_PROMPT, COLORING_PAGES

# Module-level client cache
_client = None


def _get_client() -> openai.OpenAI:
    """Return a cached OpenAI client (reads OPENAI_API_KEY from env)."""
    global _client
    if _client is None:
        _client = openai.OpenAI()
    return _client


def retry_api_call(fn, *, max_retries: int = RETRY_MAX, base_delay: float = RETRY_BASE_DELAY):
    """Execute fn() with exponential backoff retry on transient API errors.

    Retries on openai.RateLimitError and openai.APIError up to max_retries
    times. Raises the last error if all retries are exhausted.
    """
    last_error = None
    for attempt in range(1 + max_retries):
        try:
            return fn()
        except (openai.RateLimitError, openai.APIError) as exc:
            last_error = exc
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"  Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {exc}")
                time.sleep(delay)
    raise last_error


def generate_image(
    prompt: str,
    output_path: str | Path,
    *,
    size: str = IMAGE_SIZE,
    quality: str = "high",
) -> Path:
    """Generate an image via gpt-image-1 and save to output_path.

    Skips generation if output_path already exists (idempotent).

    Args:
        prompt: Text prompt for image generation.
        output_path: Where to write the generated PNG.
        size: Image dimensions (e.g. "1024x1024").
        quality: Generation quality ("high", "medium", "low").

    Returns:
        The output_path as a Path object.
    """
    output_path = Path(output_path)

    if output_path.exists():
        print(f"  Skip (exists): {output_path.name}")
        return output_path

    client = _get_client()

    def _call():
        return client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality=quality,
        )

    response = retry_api_call(_call)

    # Decode b64_json response and write to file
    image_b64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    print(f"  Generated: {output_path.name}")

    return output_path


def generate_coloring_pages() -> list[Path]:
    """Generate all 4 coloring page PNGs.

    Each page combines the COLORING_BASE_PROMPT with a page-specific
    detail prompt. Output goes to GENERATED_PNG_DIR / "coloring" / "<id>.png".

    Returns:
        List of output Path objects for each generated image.
    """
    output_dir = GENERATED_PNG_DIR / "coloring"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for page in COLORING_PAGES:
        full_prompt = COLORING_BASE_PROMPT + page["prompt_detail"]
        out = output_dir / f"{page['id']}.png"
        result = generate_image(full_prompt, out)
        results.append(result)

    return results
