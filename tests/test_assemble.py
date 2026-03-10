"""Tests for SVG assembly and frontend asset copy."""

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest


# SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

# All expected variant IDs in defs
VARIANT_IDS = [
    "tail-1", "tail-2", "tail-3",
    "hair-1", "hair-2", "hair-3",
    "acc-1", "acc-2", "acc-3",
]


@pytest.fixture
def traced_parts_dir(tmp_path) -> Path:
    """Create mock traced SVG files simulating vtracer output.

    Creates simple SVGs with path elements named tail-1.svg through acc-3.svg.
    """
    parts_dir = tmp_path / "traced_parts"
    parts_dir.mkdir()

    for variant_id in VARIANT_IDS:
        svg_content = (
            f'<svg xmlns="{SVG_NS}" viewBox="0 0 1024 1024">'
            f'<path d="M10,10 L100,100 L10,100 Z" fill="#aabbcc" />'
            f'</svg>'
        )
        (parts_dir / f"{variant_id}.svg").write_text(svg_content)

    return parts_dir


@pytest.fixture
def assembled_svg(traced_parts_dir, tmp_path) -> tuple[Path, ET.Element]:
    """Run assemble_mermaid_svg() and return (output_path, parsed_root)."""
    from mermaids.pipeline.assemble import assemble_mermaid_svg

    output = tmp_path / "mermaid.svg"
    assemble_mermaid_svg(traced_parts_dir, output)

    tree = ET.parse(output)
    root = tree.getroot()
    return output, root


# -------------------------------------------------------
# SVG assembly tests
# -------------------------------------------------------


class TestAssembleMermaidSvg:
    """Tests for assemble_mermaid_svg()."""

    def test_assemble_creates_svg_with_defs(self, assembled_svg):
        """assemble_mermaid_svg() produces SVG with a <defs> element."""
        output, root = assembled_svg
        assert output.exists()

        defs = root.find(f"{{{SVG_NS}}}defs")
        assert defs is not None, "SVG should contain a <defs> element"

    def test_assemble_has_all_variant_ids(self, assembled_svg):
        """Assembled SVG contains g elements with all variant IDs in defs."""
        _, root = assembled_svg

        defs = root.find(f"{{{SVG_NS}}}defs")
        g_ids = set()
        for g in defs.findall(f"{{{SVG_NS}}}g"):
            gid = g.get("id")
            if gid:
                g_ids.add(gid)

        for variant_id in VARIANT_IDS:
            assert variant_id in g_ids, f"Missing variant group id={variant_id} in defs"

    def test_assemble_has_acc_none(self, assembled_svg):
        """Assembled SVG contains g element with id acc-none (empty with hit-area rect)."""
        _, root = assembled_svg

        defs = root.find(f"{{{SVG_NS}}}defs")
        acc_none = None
        for g in defs.findall(f"{{{SVG_NS}}}g"):
            if g.get("id") == "acc-none":
                acc_none = g
                break

        assert acc_none is not None, "Missing <g id='acc-none'> in defs"
        # Should have a rect child (hit-area)
        rect = acc_none.find(f"{{{SVG_NS}}}rect")
        assert rect is not None, "acc-none should have a <rect> hit-area"

    def test_assemble_has_use_elements(self, assembled_svg):
        """Assembled SVG contains use elements with correct IDs and default hrefs."""
        _, root = assembled_svg

        # Find all use elements (may be nested in groups)
        uses = root.iter(f"{{{SVG_NS}}}use")
        use_map = {}
        for use in uses:
            uid = use.get("id")
            if uid:
                href = use.get("href") or use.get(f"{{{XLINK_NS}}}href")
                use_map[uid] = href

        assert "active-tail" in use_map, "Missing <use id='active-tail'>"
        assert "active-hair" in use_map, "Missing <use id='active-hair'>"
        assert "active-acc" in use_map, "Missing <use id='active-acc'>"

        assert use_map["active-tail"] == "#tail-1"
        assert use_map["active-hair"] == "#hair-1"
        assert use_map["active-acc"] == "#acc-none"

    def test_assemble_has_body_group(self, assembled_svg):
        """Assembled SVG contains a body group with data-region='body'."""
        _, root = assembled_svg

        found = False
        for g in root.iter(f"{{{SVG_NS}}}g"):
            if g.get("data-region") == "body":
                found = True
                break

        assert found, "Missing <g data-region='body'> body group"

    def test_assemble_has_face_details(self, assembled_svg):
        """Assembled SVG contains face elements (eyes, smile, cheeks) outside
        the watercolor filter group."""
        output, _ = assembled_svg
        content = output.read_text()

        # Should contain ellipse for eyes and circles for cheeks/sparkles
        assert "ellipse" in content.lower() or "circle" in content.lower(), \
            "SVG should contain face detail elements (ellipse/circle for eyes/cheeks)"

    def test_assemble_viewbox(self, assembled_svg):
        """Assembled SVG has viewBox='0 0 400 700'."""
        _, root = assembled_svg
        viewbox = root.get("viewBox")
        assert viewbox == "0 0 400 700", f"Expected viewBox='0 0 400 700', got '{viewbox}'"

    def test_assembled_svg_valid_xml(self, assembled_svg):
        """Output mermaid.svg parses as valid XML."""
        output, _ = assembled_svg
        # If we got here, ET.parse already succeeded in the fixture.
        # Double-check by reading raw text and parsing again.
        content = output.read_text()
        root = ET.fromstring(content)
        assert root.tag.endswith("svg")


# -------------------------------------------------------
# Copy functions tests
# -------------------------------------------------------


class TestCopyFunctions:
    """Tests for copy_coloring_pages_to_frontend and copy_mermaid_to_frontend."""

    def test_copy_coloring_pages(self, tmp_path):
        """copy_coloring_pages_to_frontend() copies SVGs from generated dir to
        frontend/assets/svg/coloring/."""
        from mermaids.pipeline.assemble import copy_coloring_pages_to_frontend

        # Set up source SVGs
        src_dir = tmp_path / "svg" / "coloring"
        src_dir.mkdir(parents=True)
        (src_dir / "page-1.svg").write_text("<svg>page1</svg>")
        (src_dir / "page-2.svg").write_text("<svg>page2</svg>")

        # Set up destination
        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with (
            patch("mermaids.pipeline.assemble.GENERATED_SVG_DIR", tmp_path / "svg"),
            patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir),
        ):
            results = copy_coloring_pages_to_frontend()

        assert len(results) == 2
        for r in results:
            assert r.exists()
        assert (dst_dir / "coloring" / "page-1.svg").exists()
        assert (dst_dir / "coloring" / "page-2.svg").exists()

    def test_copy_mermaid_to_frontend(self, tmp_path):
        """copy_mermaid_to_frontend() copies assembled mermaid.svg to
        frontend/assets/svg/mermaid.svg."""
        from mermaids.pipeline.assemble import copy_mermaid_to_frontend

        # Create source SVG
        src = tmp_path / "assembled" / "mermaid.svg"
        src.parent.mkdir(parents=True)
        src.write_text("<svg>assembled</svg>")

        # Set up destination
        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir):
            result = copy_mermaid_to_frontend(src)

        assert result.exists()
        assert result == dst_dir / "mermaid.svg"
        assert result.read_text() == "<svg>assembled</svg>"
