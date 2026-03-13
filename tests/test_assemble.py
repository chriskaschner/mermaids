"""Tests for SVG assembly and frontend asset copy."""

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest


# SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

# All expected variant IDs in defs (12 parts + body)
VARIANT_IDS = [
    "tail-1", "tail-2", "tail-3",
    "hair-1", "hair-2", "hair-3",
    "eye-1", "eye-2", "eye-3",
    "acc-1", "acc-2", "acc-3",
]

# Expected 5-layer stacking order (tail=back, acc=top)
LAYER_ORDER = ["active-tail", "active-body", "active-hair", "active-eyes", "active-acc"]


@pytest.fixture
def traced_parts_dir(tmp_path) -> Path:
    """Create mock traced SVG files simulating vtracer output.

    Creates simple SVGs with path elements named tail-1.svg through acc-3.svg,
    plus a body.svg for the static base body.
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

    # Base body SVG
    body_svg = (
        f'<svg xmlns="{SVG_NS}" viewBox="0 0 1024 1024">'
        f'<path d="M200,200 L800,200 L800,800 L200,800 Z" fill="#ffd0b0" />'
        f'</svg>'
    )
    (parts_dir / "body.svg").write_text(body_svg)

    return parts_dir


@pytest.fixture
def assembled_svg(traced_parts_dir, tmp_path) -> tuple[Path, ET.Element]:
    """Run assemble_mermaid_svg() and return (output_path, parsed_root)."""
    from mermaids.pipeline.assemble import assemble_mermaid_svg

    output = tmp_path / "mermaid.svg"
    base_svg = traced_parts_dir / "body.svg"
    assemble_mermaid_svg(traced_parts_dir, output, base_traced_svg=base_svg)

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
        """Assembled SVG contains g elements with all 12 variant IDs + body in defs."""
        _, root = assembled_svg

        defs = root.find(f"{{{SVG_NS}}}defs")
        g_ids = set()
        for g in defs.findall(f"{{{SVG_NS}}}g"):
            gid = g.get("id")
            if gid:
                g_ids.add(gid)

        for variant_id in VARIANT_IDS:
            assert variant_id in g_ids, f"Missing variant group id={variant_id} in defs"

        # Body group must also be present
        assert "body" in g_ids, "Missing 'body' group in defs"

    def test_body_group_in_defs(self, assembled_svg):
        """Assembled SVG has a 'body' group in defs containing base body paths."""
        _, root = assembled_svg

        defs = root.find(f"{{{SVG_NS}}}defs")
        body_group = None
        for g in defs.findall(f"{{{SVG_NS}}}g"):
            if g.get("id") == "body":
                body_group = g
                break

        assert body_group is not None, "Expected a <g id='body'> group in defs"
        # Should have at least one child path from the base body SVG
        children = list(body_group)
        assert len(children) >= 1, "Body group should contain at least one child element"

    def test_assemble_has_five_use_elements(self, assembled_svg):
        """Assembled SVG has exactly 5 <use> elements with correct IDs."""
        _, root = assembled_svg

        uses = list(root.iter(f"{{{SVG_NS}}}use"))
        assert len(uses) == 5, f"Expected 5 <use> elements, got {len(uses)}"

        use_ids = {u.get("id") for u in uses}
        assert use_ids == {"active-tail", "active-body", "active-hair", "active-eyes", "active-acc"}, (
            f"Expected 5 use IDs, got {use_ids}"
        )

    def test_layer_stacking_order(self, assembled_svg):
        """Use elements appear in DOM order: tail (back) > body > hair > eyes > acc (top)."""
        _, root = assembled_svg

        uses = [e for e in root if e.tag == f"{{{SVG_NS}}}use"]
        use_ids = [u.get("id") for u in uses]

        assert use_ids == LAYER_ORDER, (
            f"Expected layer order {LAYER_ORDER}, got {use_ids}"
        )

    def test_active_tail_references_tail1(self, assembled_svg):
        """active-tail use element references #tail-1 by default."""
        _, root = assembled_svg

        uses = {u.get("id"): u for u in root.iter(f"{{{SVG_NS}}}use")}
        active_tail = uses.get("active-tail")
        assert active_tail is not None, "Expected active-tail use element"

        href = active_tail.get("href") or active_tail.get(f"{{{XLINK_NS}}}href")
        assert href == "#tail-1", f"Expected active-tail href=#tail-1, got {href}"

    def test_active_body_references_body(self, assembled_svg):
        """active-body use element references the static #body group."""
        _, root = assembled_svg

        uses = {u.get("id"): u for u in root.iter(f"{{{SVG_NS}}}use")}
        active_body = uses.get("active-body")
        assert active_body is not None, "Expected active-body use element"

        href = active_body.get("href") or active_body.get(f"{{{XLINK_NS}}}href")
        assert href == "#body", f"Expected active-body href=#body, got {href}"

    def test_data_category_attributes(self, assembled_svg):
        """Swappable use elements have data-category attribute; active-body does not."""
        _, root = assembled_svg

        uses = {u.get("id"): u for u in root.iter(f"{{{SVG_NS}}}use")}

        assert uses["active-tail"].get("data-category") == "tail"
        assert uses["active-hair"].get("data-category") == "hair"
        assert uses["active-eyes"].get("data-category") == "eyes"
        assert uses["active-acc"].get("data-category") == "acc"
        # active-body has no data-category (static, never swapped)
        assert uses["active-body"].get("data-category") is None

    def test_assemble_viewbox(self, assembled_svg):
        """Assembled SVG has square viewBox matching 1024x1024 traced source."""
        _, root = assembled_svg
        viewbox = root.get("viewBox")
        assert viewbox == "0 0 1024 1024", f"Expected viewBox='0 0 1024 1024', got '{viewbox}'"

    def test_assembled_svg_valid_xml(self, assembled_svg):
        """Output mermaid.svg parses as valid XML."""
        output, _ = assembled_svg
        content = output.read_text()
        root = ET.fromstring(content)
        assert root.tag.endswith("svg")

    def test_defs_has_thirteen_groups(self, assembled_svg):
        """Defs contain 13 groups: 12 variant parts + 1 body."""
        _, root = assembled_svg

        defs = root.find(f"{{{SVG_NS}}}defs")
        g_elements = defs.findall(f"{{{SVG_NS}}}g")
        assert len(g_elements) == 13, (
            f"Expected 13 groups in defs (12 parts + body), got {len(g_elements)}"
        )


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


# -------------------------------------------------------
# Copy dressup parts tests (updated for 12 variants)
# -------------------------------------------------------


class TestCopyDressupParts:
    """Tests for copy_dressup_parts_to_frontend()."""

    def test_copies_all_twelve_variants(self, tmp_path):
        """copy_dressup_parts_to_frontend() copies 12 SVGs from generated
        dressup dir to frontend/assets/svg/dressup/."""
        from mermaids.pipeline.assemble import copy_dressup_parts_to_frontend

        # Set up source SVGs
        src_dir = tmp_path / "svg" / "dressup"
        src_dir.mkdir(parents=True)
        for variant_id in VARIANT_IDS:
            (src_dir / f"{variant_id}.svg").write_text(
                f'<svg xmlns="{SVG_NS}"><path d="M1 1" fill="#abc"/></svg>'
            )

        # Set up destination
        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with (
            patch("mermaids.pipeline.assemble.GENERATED_SVG_DIR", tmp_path / "svg"),
            patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir),
        ):
            results = copy_dressup_parts_to_frontend()

        assert len(results) == 12, f"Expected 12 copied files, got {len(results)}"
        for r in results:
            assert r.exists()
        for variant_id in VARIANT_IDS:
            assert (dst_dir / "dressup" / f"{variant_id}.svg").exists()

    def test_copies_no_source_dir(self, tmp_path):
        """copy_dressup_parts_to_frontend() returns empty list when source
        dir does not exist."""
        from mermaids.pipeline.assemble import copy_dressup_parts_to_frontend

        # Point to a non-existent source directory
        fake_src = tmp_path / "nonexistent"
        dst_dir = tmp_path / "frontend" / "assets" / "svg"
        dst_dir.mkdir(parents=True)

        with (
            patch("mermaids.pipeline.assemble.GENERATED_SVG_DIR", fake_src),
            patch("mermaids.pipeline.assemble.FRONTEND_SVG_DIR", dst_dir),
        ):
            results = copy_dressup_parts_to_frontend()

        assert results == []


# -------------------------------------------------------
# Background rect stripping tests
# -------------------------------------------------------


class TestBackgroundStrip:
    """Tests for background-rect stripping in _make_variant_group()."""

    @pytest.fixture
    def traced_with_bg_dir(self, tmp_path) -> Path:
        """Create traced SVGs with a near-white background path as first child."""
        parts_dir = tmp_path / "traced_bg"
        parts_dir.mkdir()

        for variant_id in VARIANT_IDS:
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
            (parts_dir / f"{variant_id}.svg").write_text(svg_content)

        # Simple body SVG without background rect
        body_svg = (
            f'<svg xmlns="{SVG_NS}" viewBox="0 0 1024 1024">'
            f'<path d="M200,200 L800,200 L800,800 L200,800 Z" fill="#ffd0b0" />'
            f'</svg>'
        )
        (parts_dir / "body.svg").write_text(body_svg)

        return parts_dir

    def test_first_path_stripped(self, traced_with_bg_dir, tmp_path):
        """assemble_mermaid_svg() strips the near-white background path from
        variant groups in defs."""
        from mermaids.pipeline.assemble import assemble_mermaid_svg

        output = tmp_path / "mermaid_bg.svg"
        base_svg = traced_with_bg_dir / "body.svg"
        assemble_mermaid_svg(traced_with_bg_dir, output, base_traced_svg=base_svg)

        tree = ET.parse(output)
        root = tree.getroot()
        defs = root.find(f"{{{SVG_NS}}}defs")

        for g in defs.findall(f"{{{SVG_NS}}}g"):
            gid = g.get("id", "")
            if gid in VARIANT_IDS:
                first_child = list(g)[0]
                fill = first_child.get("fill", "").upper()
                assert not fill.startswith(("#FE", "#FF", "#FD")), (
                    f"Background rect not stripped in {gid}: "
                    f"first child fill={fill}"
                )

    def test_non_background_paths_preserved(self, traced_with_bg_dir, tmp_path):
        """Variant groups retain all non-background path elements."""
        from mermaids.pipeline.assemble import assemble_mermaid_svg

        output = tmp_path / "mermaid_bg.svg"
        base_svg = traced_with_bg_dir / "body.svg"
        assemble_mermaid_svg(traced_with_bg_dir, output, base_traced_svg=base_svg)

        tree = ET.parse(output)
        root = tree.getroot()
        defs = root.find(f"{{{SVG_NS}}}defs")

        for g in defs.findall(f"{{{SVG_NS}}}g"):
            gid = g.get("id", "")
            if gid in VARIANT_IDS:
                children = list(g)
                # Should have 2 remaining paths (bg stripped, 2 content paths remain)
                assert len(children) == 2, (
                    f"Expected 2 children in {gid} after bg strip, "
                    f"got {len(children)}"
                )
                fills = [c.get("fill", "").lower() for c in children]
                assert "#aabbcc" in fills, (
                    f"Missing content path fill=#aabbcc in {gid}"
                )
                assert "#dd3344" in fills, (
                    f"Missing content path fill=#dd3344 in {gid}"
                )
