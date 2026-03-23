"""Mask creation and OpenAI edit API wrapper for region-based image editing.

Provides create_region_mask() for building RGBA masks and edit_region() for
calling the gpt-image-1 edit endpoint to replace a masked region of an image.
"""

import base64
import io
from pathlib import Path

import openai
from PIL import Image

from mermaids.pipeline.config import (
    IMAGE_SIZE,
)
from mermaids.pipeline.generate import retry_api_call

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
# Regions are designed to be non-overlapping (fixes DEBT-03).
#
# Vertical layout (top -> bottom):
#   hair:  upper head/crown zone -- y: 0..290
#   eyes:  face-center zone -- y: 300..440
#   acc:   torso/collar zone (necklaces, wands, companions) -- y: 450..549
#   tail:  lower body -- y: 550..1024 (hair y2=290 < tail y1=550)
#
# No pair of regions share any pixel area.
REGIONS: dict[str, tuple[int, int, int, int]] = {
    "hair": (150, 0,   874, 290),   # upper head, crown and hair
    "eyes": (300, 300, 724, 440),   # face-center, eye area
    "acc":  (200, 450, 824, 549),   # torso/collar for necklaces, wands, companions
    "tail": (200, 550, 824, 1024),  # lower body, well below all above regions
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
