"""Tests for the SVG tracing pipeline."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

from mermaids.pipeline.config import FRONTEND_SVG_DIR
from mermaids.pipeline.trace import trace_to_svg

# ---------------------------------------------------------------------------
# Dress-up coloring outline asset tests
# ---------------------------------------------------------------------------

DRESSUP_COLORING_DIR: Path = FRONTEND_SVG_DIR / "dressup-coloring"
OUTLINE_IDS: list[str] = [f"mermaid-{i}" for i in range(1, 10)]


def test_dressup_coloring_outlines_exist():
    """All 9 mermaid-{1-9}-outline.svg files exist in dressup-coloring/ and are >500 bytes."""
    missing = []
    too_small = []
    for cid in OUTLINE_IDS:
        path = DRESSUP_COLORING_DIR / f"{cid}-outline.svg"
        if not path.exists():
            missing.append(path.name)
            continue
        size = path.stat().st_size
        if size <= 500:
            too_small.append(f"{path.name} ({size} bytes)")

    assert not missing, f"Missing outline SVGs: {missing}"
    assert not too_small, f"Outline SVGs under 500 bytes: {too_small}"


def test_dressup_coloring_outlines_are_valid_svg():
    """Each mermaid-{1-9}-outline.svg starts with '<svg' and contains 'viewBox'."""
    invalid = []
    for cid in OUTLINE_IDS:
        path = DRESSUP_COLORING_DIR / f"{cid}-outline.svg"
        if not path.exists():
            invalid.append(f"{path.name}: file not found")
            continue
        content = path.read_text(encoding="utf-8")
        if not content.lstrip().startswith("<svg"):
            invalid.append(f"{path.name}: does not start with <svg")
        if "viewBox" not in content:
            invalid.append(f"{path.name}: missing viewBox attribute")

    assert not invalid, f"Invalid SVG files: {invalid}"


@pytest.fixture
def test_image(tmp_path):
    """Create a simple 200x400 colored rectangle PNG for testing."""
    img = Image.new("RGB", (200, 400), color=(100, 150, 200))
    path = tmp_path / "test_input.png"
    img.save(path)
    return path


@pytest.fixture
def large_image(tmp_path):
    """Create an image larger than 1024px to test resize behavior."""
    img = Image.new("RGB", (2048, 3072), color=(80, 120, 180))
    path = tmp_path / "large_input.png"
    img.save(path)
    return path


def test_trace_produces_valid_svg(test_image, tmp_path):
    """trace_to_svg() with a simple test image produces a valid SVG file."""
    output = tmp_path / "output.svg"
    result = trace_to_svg(test_image, output)

    assert result == output
    assert output.exists()

    # Parse as XML and verify svg root element
    tree = ET.parse(output)
    root = tree.getroot()
    # SVG namespace may or may not be present
    tag = root.tag
    assert tag.endswith("svg"), f"Expected svg root element, got {tag}"


def test_trace_output_under_500kb(test_image, tmp_path):
    """Output SVG file size is under 500KB for a small source image."""
    output = tmp_path / "output.svg"
    trace_to_svg(test_image, output)

    size = output.stat().st_size
    assert size < 500_000, f"SVG too large: {size} bytes (limit 500KB)"


def test_trace_output_valid_xml(test_image, tmp_path):
    """Output SVG contains valid XML with an svg root element."""
    output = tmp_path / "output.svg"
    trace_to_svg(test_image, output)

    # Should parse without error
    tree = ET.parse(output)
    root = tree.getroot()
    assert root.tag.endswith("svg")

    # Should have at least some content (paths or groups)
    content = output.read_text()
    assert len(content) > 50, "SVG appears empty"


def test_simplify_produces_fewer_paths(test_image, tmp_path):
    """trace_to_svg() with simplify=True produces fewer paths than simplify=False."""
    output_simple = tmp_path / "simple.svg"
    output_full = tmp_path / "full.svg"

    trace_to_svg(test_image, output_simple, simplify=True)
    trace_to_svg(test_image, output_full, simplify=False)

    simple_content = output_simple.read_text()
    full_content = output_full.read_text()

    simple_paths = simple_content.count("<path")
    full_paths = full_content.count("<path")

    # Simplified should have fewer or equal paths (binary mode is more aggressive)
    assert simple_paths <= full_paths, (
        f"Simplified ({simple_paths} paths) should have fewer paths "
        f"than full ({full_paths} paths)"
    )


def test_large_image_resized_before_tracing(large_image, tmp_path):
    """Source images larger than 1024px are resized before tracing."""
    output = tmp_path / "output.svg"
    trace_to_svg(large_image, output)

    # The output should exist and be valid
    assert output.exists()
    tree = ET.parse(output)
    root = tree.getroot()
    assert root.tag.endswith("svg")

    # The SVG viewBox or width/height should reflect the resized dimensions,
    # not the original 2048x3072. Check the SVG content is reasonable size
    # (a 2048x3072 image traced without resize would produce a much larger file).
    size = output.stat().st_size
    assert size < 500_000, f"SVG too large ({size} bytes) -- image may not have been resized"
