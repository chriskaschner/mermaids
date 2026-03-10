"""Mask creation and OpenAI edit API wrapper for dress-up variant generation.

Provides create_region_mask() for building RGBA masks, edit_region() for
calling the gpt-image-1 edit endpoint, and generate_dressup_variants() to
produce all 9 dress-up part PNGs (3 tails, 3 hair, 3 accessories).
"""

import base64
import io
from pathlib import Path

import openai
from PIL import Image

from mermaids.pipeline.config import (
    GENERATED_PNG_DIR,
    IMAGE_SIZE,
    RETRY_BASE_DELAY,
    RETRY_MAX,
)
from mermaids.pipeline.generate import generate_image, retry_api_call
from mermaids.pipeline.prompts import DRESSUP_BASE_PROMPT, DRESSUP_VARIANTS

# Module-level client cache (separate from generate.py's client)
_client = None


def _get_client() -> openai.OpenAI:
    """Return a cached OpenAI client (reads OPENAI_API_KEY from env)."""
    global _client
    if _client is None:
        _client = openai.OpenAI()
    return _client


# Region coordinate definitions for 1024x1024 generation space.
# Transparent area = area to be replaced by the edit API.
REGIONS: dict[str, tuple[int, int, int, int]] = {
    "tail": (200, 500, 824, 1024),   # lower body area
    "hair": (200, 0, 824, 350),       # head/hair area
    "acc":  (300, 0, 724, 250),       # top of head for accessories
}

# Map DRESSUP_VARIANTS category keys to region keys
_CATEGORY_TO_REGION: dict[str, str] = {
    "tails": "tail",
    "hair": "hair",
    "accessories": "acc",
}


def create_region_mask(
    image_size: tuple[int, int],
    region_bbox: tuple[int, int, int, int],
) -> bytes:
    """Create an RGBA PNG mask for the OpenAI edit API.

    The mask is opaque (alpha=255) everywhere except inside region_bbox,
    where it is transparent (alpha=0). Per OpenAI semantics, transparent
    areas are the regions to be replaced.

    Args:
        image_size: (width, height) of the output mask.
        region_bbox: (x1, y1, x2, y2) bounding box of the edit region.

    Returns:
        PNG bytes of the RGBA mask.
    """
    width, height = image_size
    x1, y1, x2, y2 = region_bbox

    # Start fully opaque (white with alpha=255)
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))

    # Make the region transparent (alpha=0) -- area to be edited
    for y in range(max(0, y1), min(height, y2)):
        for x in range(max(0, x1), min(width, x2)):
            img.putpixel((x, y), (0, 0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def edit_region(
    base_image_path: Path,
    mask_bytes: bytes,
    prompt: str,
    output_path: Path,
    *,
    size: str = IMAGE_SIZE,
) -> Path:
    """Call the OpenAI edit API to replace a masked region of the base image.

    Skips if output_path already exists (idempotent). Uses retry_api_call
    for transient error handling.

    Args:
        base_image_path: Path to the base mermaid PNG.
        mask_bytes: RGBA PNG bytes of the mask (transparent = edit region).
        prompt: Text prompt describing the desired replacement.
        output_path: Where to write the resulting PNG.
        size: Image dimensions for the edit output.

    Returns:
        The output_path as a Path object.
    """
    output_path = Path(output_path)

    if output_path.exists():
        print(f"  Skip (exists): {output_path.name}")
        return output_path

    client = _get_client()

    # Prepare file-like objects for the API call
    image_file = open(base_image_path, "rb")
    mask_file = io.BytesIO(mask_bytes)
    mask_file.name = "mask.png"

    def _call():
        # Reset file positions for retry
        image_file.seek(0)
        mask_file.seek(0)
        return client.images.edit(
            model="gpt-image-1",
            image=image_file,
            mask=mask_file,
            prompt=prompt,
            size=size,
        )

    try:
        response = retry_api_call(_call)
    finally:
        image_file.close()

    # Decode b64_json response and write to file
    image_b64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    print(f"  Generated: {output_path.name}")

    return output_path


def generate_base_mermaid() -> Path:
    """Generate the full-color base mermaid image for dress-up editing.

    Uses generate_image() from generate.py with DRESSUP_BASE_PROMPT.
    Output goes to GENERATED_PNG_DIR / "dressup" / "base" / "mermaid-base.png".
    Skips if the file already exists (idempotent).

    Returns:
        Path to the base mermaid PNG.
    """
    output_path = GENERATED_PNG_DIR / "dressup" / "base" / "mermaid-base.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return generate_image(DRESSUP_BASE_PROMPT, output_path)


def generate_dressup_variants() -> list[Path]:
    """Generate all 9 dress-up variant PNGs via the edit API.

    1. Generates (or skips) the base mermaid image.
    2. For each category (tails, hair, accessories):
       a. Creates a mask for that region.
       b. For each variant, calls edit_region() with the variant prompt.
    3. Returns list of all generated variant paths.

    Returns:
        List of 9 Path objects (tail-1..3, hair-1..3, acc-1..3).
    """
    print("Generating base mermaid for dress-up...")
    base_path = generate_base_mermaid()

    # Get image dimensions for mask creation
    with Image.open(base_path) as img:
        image_size = img.size

    parts_dir = GENERATED_PNG_DIR / "dressup" / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for category_key, variants in DRESSUP_VARIANTS.items():
        region_key = _CATEGORY_TO_REGION[category_key]
        region_bbox = REGIONS[region_key]

        print(f"\nGenerating {category_key} variants (region: {region_key})...")
        mask_bytes = create_region_mask(image_size, region_bbox)

        for variant in variants:
            variant_id = variant["id"]
            prompt = DRESSUP_BASE_PROMPT + variant["prompt_detail"]
            output = parts_dir / f"{variant_id}.png"

            print(f"  Variant: {variant_id}")
            result = edit_region(base_path, mask_bytes, prompt, output)
            results.append(result)

    return results
