"""Tests for coloring page PNG-to-SVG tracing pipeline."""

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image, ImageDraw

from mermaids.pipeline.trace import trace_to_svg


@pytest.fixture
def coloring_page_png(tmp_path) -> Path:
    """Create a simple B&W test PNG simulating a coloring page.

    200x200 white background with a black circle outline, similar to
    what a generated coloring page would look like.
    """
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw a black circle outline (simulates coloring page line art)
    draw.ellipse([30, 30, 170, 170], outline=(0, 0, 0), width=4)
    # Add a smaller inner shape for more path variety
    draw.rectangle([70, 70, 130, 130], outline=(0, 0, 0), width=3)

    path = tmp_path / "coloring_test.png"
    img.save(path)
    return path


class TestTraceColoringPage:
    """Tests for tracing coloring page PNGs to SVGs."""

    def test_trace_coloring_page_produces_svg(self, coloring_page_png, tmp_path):
        """Tracing a coloring page PNG (binary mode) produces valid SVG with
        path elements."""
        output = tmp_path / "traced.svg"
        result = trace_to_svg(coloring_page_png, output, simplify=True)

        assert result == output
        assert output.exists()

        # Parse as XML, verify SVG root
        tree = ET.parse(output)
        root = tree.getroot()
        assert root.tag.endswith("svg"), f"Expected svg root, got {root.tag}"

        # Should have at least one path element
        content = output.read_text()
        assert "<path" in content, "SVG should contain path elements"

    def test_trace_coloring_page_uses_simplify_true(self, coloring_page_png, tmp_path):
        """Coloring pages are traced with simplify=True (binary mode) which
        produces fewer, cleaner paths than color mode."""
        simple_out = tmp_path / "simple.svg"
        color_out = tmp_path / "color.svg"

        trace_to_svg(coloring_page_png, simple_out, simplify=True)
        trace_to_svg(coloring_page_png, color_out, simplify=False)

        simple_paths = simple_out.read_text().count("<path")
        color_paths = color_out.read_text().count("<path")

        # Binary mode (simplify=True) should produce fewer or equal paths
        assert simple_paths <= color_paths, (
            f"simplify=True ({simple_paths} paths) should have <= paths "
            f"than simplify=False ({color_paths} paths)"
        )

    def test_traced_svg_under_500kb(self, coloring_page_png, tmp_path):
        """Traced coloring page SVGs are under 500KB."""
        output = tmp_path / "traced.svg"
        trace_to_svg(coloring_page_png, output, simplify=True)

        size = output.stat().st_size
        assert size < 500_000, f"SVG too large: {size} bytes (limit 500KB)"


class TestTraceAllColoring:
    """Tests for the trace_all.py coloring page tracing workflow."""

    def test_trace_all_coloring_skips_existing(self, coloring_page_png, tmp_path):
        """trace_coloring_pages() skips files where output SVG already exists."""
        import importlib.util
        import shutil

        # Set up directory structure matching what trace_all expects
        png_dir = tmp_path / "png" / "coloring"
        svg_dir = tmp_path / "svg" / "coloring"
        png_dir.mkdir(parents=True)
        svg_dir.mkdir(parents=True)

        # Copy test PNG into the expected location
        test_png = png_dir / "page-1-ocean.png"
        shutil.copy2(coloring_page_png, test_png)

        # Pre-create the output SVG (should be skipped)
        existing_svg = svg_dir / "page-1-ocean.svg"
        existing_svg.write_text("<svg>pre-existing</svg>")
        original_content = existing_svg.read_text()

        # Load trace_all module from file path (not installed as a package)
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "trace_all.py"
        spec = importlib.util.spec_from_file_location("trace_all", script_path)
        trace_mod = importlib.util.module_from_spec(spec)

        # Patch config paths before executing the module
        with (
            patch("mermaids.pipeline.config.GENERATED_PNG_DIR", tmp_path / "png"),
            patch("mermaids.pipeline.config.GENERATED_SVG_DIR", tmp_path / "svg"),
        ):
            spec.loader.exec_module(trace_mod)

            # After exec, the module-level imports captured the patched values,
            # but we also need to patch the module's own references
            trace_mod.GENERATED_PNG_DIR = tmp_path / "png"
            trace_mod.GENERATED_SVG_DIR = tmp_path / "svg"

            results = trace_mod.trace_coloring_pages()

        # The pre-existing SVG should not have been overwritten
        assert existing_svg.read_text() == original_content


class TestColoringSVGAssets:
    """Verify all 9 coloring page SVGs exist in the frontend directory."""

    def test_all_nine_coloring_svgs_exist(self):
        """All 9 coloring page SVGs are deployed to frontend/assets/svg/coloring/."""
        from pathlib import Path
        svg_dir = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "svg" / "coloring"
        svg_files = sorted(svg_dir.glob("page-*.svg"))
        assert len(svg_files) >= 9, f"Expected 9 coloring SVGs, found {len(svg_files)}: {[f.name for f in svg_files]}"

    def test_all_coloring_svgs_have_real_art(self):
        """All 9 coloring SVGs contain >= 5 <path elements (real art, not 1x1 placeholder)."""
        svg_dir = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "svg" / "coloring"
        failing = []
        for svg_file in sorted(svg_dir.glob("page-*.svg")):
            content = svg_file.read_text(encoding="utf-8")
            path_count = content.count("<path")
            if path_count < 5:
                failing.append(f"{svg_file.name}: {path_count} paths")
        assert not failing, f"SVGs with insufficient paths (real art needs >= 5): {failing}"
