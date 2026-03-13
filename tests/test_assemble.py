"""Tests for SVG assembly and frontend asset deployment."""

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest


SVG_NS = "http://www.w3.org/2000/svg"


# -------------------------------------------------------
# assemble_combo_svg tests (character SVG assembly)
# -------------------------------------------------------


class TestAssembleComboSvg:
    """Tests for assemble_combo_svg() -- strips bg, adds id, wraps in proper structure."""

    @pytest.fixture
    def traced_svg(self, tmp_path) -> Path:
        """Create a mock traced SVG with a near-white background path."""
        svg_content = (
            f'<svg xmlns="{SVG_NS}" viewBox="0 0 1024 1024">'
            f'<path d="M0 0 C337.92 0 675.84 0 1024 0 '
            f'C1024 337.92 1024 675.84 1024 1024 '
            f'C686.08 1024 348.16 1024 0 1024 '
            f'C0 686.08 0 348.16 0 0 Z" fill="#FEFEFE" />'
            f'<path d="M10,10 L100,100 L10,100 Z" fill="#aabbcc" />'
            f'<path d="M20,20 L200,200 L20,200 Z" fill="#dd3344" />'
            f'</svg>'
        )
        path = tmp_path / "mermaid-1.svg"
        path.write_text(svg_content)
        return path

    def test_creates_valid_svg(self, traced_svg, tmp_path):
        """Output is valid XML with an svg root element."""
        from mermaids.pipeline.assemble import assemble_combo_svg

        output = tmp_path / "out.svg"
        assemble_combo_svg(traced_svg, output)

        root = ET.fromstring(output.read_text())
        assert root.tag.endswith("svg")

    def test_has_mermaid_svg_id(self, traced_svg, tmp_path):
        """Output SVG has id='mermaid-svg'."""
        from mermaids.pipeline.assemble import assemble_combo_svg

        output = tmp_path / "out.svg"
        assemble_combo_svg(traced_svg, output)

        root = ET.fromstring(output.read_text())
        assert root.get("id") == "mermaid-svg"

    def test_has_viewbox(self, traced_svg, tmp_path):
        """Output SVG has viewBox='0 0 1024 1024'."""
        from mermaids.pipeline.assemble import assemble_combo_svg

        output = tmp_path / "out.svg"
        assemble_combo_svg(traced_svg, output)

        root = ET.fromstring(output.read_text())
        assert root.get("viewBox") == "0 0 1024 1024"

    def test_strips_background_rect(self, traced_svg, tmp_path):
        """Near-white background path is stripped from output."""
        from mermaids.pipeline.assemble import assemble_combo_svg

        output = tmp_path / "out.svg"
        assemble_combo_svg(traced_svg, output)

        root = ET.fromstring(output.read_text())
        paths = list(root.iter(f"{{{SVG_NS}}}path"))
        # Original had 3 paths (1 bg + 2 content); output should have 2
        assert len(paths) == 2, f"Expected 2 paths after bg strip, got {len(paths)}"
        fills = [p.get("fill", "").lower() for p in paths]
        assert "#aabbcc" in fills
        assert "#dd3344" in fills

    def test_preserves_content_paths(self, traced_svg, tmp_path):
        """Non-background paths are preserved in output."""
        from mermaids.pipeline.assemble import assemble_combo_svg

        output = tmp_path / "out.svg"
        assemble_combo_svg(traced_svg, output)

        root = ET.fromstring(output.read_text())
        paths = list(root.iter(f"{{{SVG_NS}}}path"))
        fills = {p.get("fill", "").lower() for p in paths}
        assert "#aabbcc" in fills, "Missing content path #aabbcc"
        assert "#dd3344" in fills, "Missing content path #dd3344"


# -------------------------------------------------------
# deploy_characters_to_frontend tests
# -------------------------------------------------------


class TestDeployCharactersToFrontend:
    """Tests for deploy_characters_to_frontend()."""

    def test_deploys_all_characters(self, tmp_path):
        """Copies mermaid-{1..9}.svg to frontend dressup dir."""
        from mermaids.pipeline.assemble import deploy_characters_to_frontend

        # Set up source SVGs
        src_dir = tmp_path / "assembled"
        src_dir.mkdir()
        for i in range(1, 10):
            (src_dir / f"mermaid-{i}.svg").write_text(f"<svg>char{i}</svg>")

        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir):
            result = deploy_characters_to_frontend(src_dir)

        assert result == dst_dir / "mermaid.svg"
        for i in range(1, 10):
            assert (dst_dir / "dressup" / f"mermaid-{i}.svg").exists()

    def test_copies_mermaid1_as_default(self, tmp_path):
        """Copies mermaid-1.svg as the default mermaid.svg."""
        from mermaids.pipeline.assemble import deploy_characters_to_frontend

        src_dir = tmp_path / "assembled"
        src_dir.mkdir()
        (src_dir / "mermaid-1.svg").write_text("<svg>default</svg>")

        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir):
            deploy_characters_to_frontend(src_dir)

        default_svg = dst_dir / "mermaid.svg"
        assert default_svg.exists()
        assert default_svg.read_text() == "<svg>default</svg>"


# -------------------------------------------------------
# Copy coloring pages tests (unchanged)
# -------------------------------------------------------


class TestCopyFunctions:
    """Tests for copy_coloring_pages_to_frontend and copy_mermaid_to_frontend."""

    def test_copy_coloring_pages(self, tmp_path):
        """copy_coloring_pages_to_frontend() copies SVGs to frontend."""
        from mermaids.pipeline.assemble import copy_coloring_pages_to_frontend

        src_dir = tmp_path / "svg" / "coloring"
        src_dir.mkdir(parents=True)
        (src_dir / "page-1.svg").write_text("<svg>page1</svg>")
        (src_dir / "page-2.svg").write_text("<svg>page2</svg>")

        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with (
            patch("mermaids.pipeline.assemble.GENERATED_SVG_DIR", tmp_path / "svg"),
            patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir),
        ):
            results = copy_coloring_pages_to_frontend()

        assert len(results) == 2
        assert (dst_dir / "coloring" / "page-1.svg").exists()
        assert (dst_dir / "coloring" / "page-2.svg").exists()

    def test_copy_mermaid_to_frontend(self, tmp_path):
        """copy_mermaid_to_frontend() copies mermaid.svg to frontend."""
        from mermaids.pipeline.assemble import copy_mermaid_to_frontend

        src = tmp_path / "assembled" / "mermaid.svg"
        src.parent.mkdir(parents=True)
        src.write_text("<svg>assembled</svg>")

        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir):
            result = copy_mermaid_to_frontend(src)

        assert result.exists()
        assert result == dst_dir / "mermaid.svg"
