"""Raster image to SVG conversion using vtracer.

Provides trace_to_svg() for converting raster images (PNG, JPEG, etc.)
to clean SVG files suitable for interactive web display.
"""

import tempfile
from pathlib import Path

import vtracer
from PIL import Image


def trace_to_svg(
    input_path: str | Path,
    output_path: str | Path,
    *,
    simplify: bool = True,
) -> Path:
    """Convert a raster image to SVG using vtracer.

    For Phase 1 proof-of-concept, uses aggressive simplification
    to produce clean, small SVGs suitable for interactive regions.

    Args:
        input_path: Path to source raster image (PNG, JPEG, etc.)
        output_path: Path where output SVG will be written.
        simplify: If True, use binary colormode and higher speckle filter
            for cleaner, simpler output. If False, use full color tracing.

    Returns:
        The output_path as a Path object.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Pre-process: resize to manageable dimensions if needed
    img = Image.open(input_path)
    max_dim = 1024
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Save preprocessed image to a temp file
    temp_fd, temp_path_str = tempfile.mkstemp(suffix=".png")
    temp_path = Path(temp_path_str)
    try:
        img.save(temp_path)

        # Trace with settings tuned for clean interactive SVG
        params = dict(
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=10,
            color_precision=4,
            layer_difference=32,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )

        if simplify:
            # For Phase 1 silhouette, binary mode produces cleanest output
            params["colormode"] = "binary"
            params["filter_speckle"] = 20

        vtracer.convert_image_to_svg_py(
            image_path=str(temp_path),
            out_path=str(output_path),
            **params,
        )
    finally:
        # Clean up temp file
        import os

        os.close(temp_fd)
        temp_path.unlink(missing_ok=True)

    return output_path
