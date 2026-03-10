"""SVG assembly combining traced parts into defs+use mermaid.svg.

Builds a new mermaid.svg with the defs+use structure that the frontend
dressup.js expects. Each variant is a complete character (not an isolated
part), so the assembled SVG uses a single <use> element that swaps between
full-character groups in <defs>.

Also provides copy utilities for deploying generated SVGs to the frontend
assets directory.
"""

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from mermaids.pipeline.config import FRONTEND_SVG_DIR, GENERATED_SVG_DIR

# SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

# Register namespace so output doesn't have ns0 prefixes
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

# Expected variant part IDs in order
VARIANT_IDS = [
    "tail-1", "tail-2", "tail-3",
    "hair-1", "hair-2", "hair-3",
    "acc-1", "acc-2", "acc-3",
]


def _is_background_path(element: ET.Element) -> bool:
    """Check if an SVG element is a vtracer background rectangle.

    vtracer always generates a full-canvas background path as the first
    child of traced SVGs. It covers 0,0 to 1024,1024 with a near-white
    fill (#FEFEFE typically). This must be stripped to prevent solid color
    blocks when the variant group is recolored in the dress-up UI.

    Heuristic: path starts with "M0 0" or "M 0 0" and fill is near-white
    (any component >= 0xF0).
    """
    tag = element.tag
    if not tag.endswith("path"):
        return False

    fill = element.get("fill", "").strip().upper()
    if not fill.startswith("#") or len(fill) != 7:
        return False

    # Parse RGB hex components
    try:
        r = int(fill[1:3], 16)
        g = int(fill[3:5], 16)
        b = int(fill[5:7], 16)
    except ValueError:
        return False

    # Near-white: all components >= 0xF0
    if r < 0xF0 or g < 0xF0 or b < 0xF0:
        return False

    # Check d-attribute starts at origin (full-canvas background)
    d = element.get("d", "").strip()
    if not (d.startswith("M0 0") or d.startswith("M 0 0")):
        return False

    return True


def _make_variant_group(variant_id: str, traced_svg_path: Path) -> ET.Element:
    """Parse a traced SVG and wrap its path/shape elements in a <g> with id.

    Each variant is a complete character traced at 1024x1024. No scaling is
    applied since the viewBox matches the source coordinate space.
    Strips the vtracer background rectangle (first near-white path covering
    the full canvas) to prevent solid color blocks when recoloring.
    """
    g = ET.Element(f"{{{SVG_NS}}}g")
    g.set("id", variant_id)

    try:
        tree = ET.parse(traced_svg_path)
        root = tree.getroot()

        # Copy child elements, skipping the first-child background rect
        first_child = True
        for child in root:
            if first_child and _is_background_path(child):
                first_child = False
                continue
            first_child = False
            g.append(child)
    except ET.ParseError:
        # If the traced SVG is malformed, create empty group
        pass

    return g




def assemble_mermaid_svg(traced_parts_dir: Path, output_path: Path) -> Path:
    """Build a mermaid.svg with defs+use structure from traced part SVGs.

    Each variant is a complete character (not an isolated part). The
    assembled SVG uses a single <use> element that the frontend swaps
    between full-character groups in <defs>.

    Args:
        traced_parts_dir: Directory containing traced SVGs (tail-1.svg, etc.)
        output_path: Where to write the assembled mermaid.svg.

    Returns:
        The output_path as a Path object.
    """
    output_path = Path(output_path)

    # Create root SVG -- square viewBox matching 1024x1024 traced source
    root = ET.Element(f"{{{SVG_NS}}}svg")
    root.set("viewBox", "0 0 1024 1024")
    root.set("preserveAspectRatio", "xMidYMid meet")
    root.set("id", "mermaid-svg")

    # Create defs
    defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")

    # Add variant groups from traced SVGs
    for variant_id in VARIANT_IDS:
        svg_file = traced_parts_dir / f"{variant_id}.svg"
        if svg_file.exists():
            g = _make_variant_group(variant_id, svg_file)
            defs.append(g)
        else:
            # Create empty placeholder group
            g = ET.SubElement(defs, f"{{{SVG_NS}}}g")
            g.set("id", variant_id)

    # Single <use> referencing the active character (default: tail-1)
    use = ET.SubElement(root, f"{{{SVG_NS}}}use")
    use.set("id", "active-character")
    use.set("href", "#tail-1")
    use.set("data-region", "character")
    use.set("pointer-events", "all")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=False)

    print(f"  Assembled: {output_path.name}")
    return output_path


def copy_coloring_pages_to_frontend() -> list[Path]:
    """Copy all traced coloring page SVGs to frontend/assets/svg/coloring/.

    Returns:
        List of destination Path objects for each copied file.
    """
    src_dir = GENERATED_SVG_DIR / "coloring"
    dst_dir = FRONTEND_SVG_DIR / "coloring"
    dst_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if not src_dir.exists():
        print(f"  No coloring SVGs found in {src_dir}")
        return results

    for svg_file in sorted(src_dir.glob("*.svg")):
        dst = dst_dir / svg_file.name
        shutil.copy2(svg_file, dst)
        print(f"  Copied: {svg_file.name} -> {dst}")
        results.append(dst)

    return results


def copy_dressup_parts_to_frontend() -> list[Path]:
    """Copy individual dressup variant SVGs to frontend/assets/svg/dressup/.

    These are the individual traced SVGs used for preview thumbnails in the
    dress-up UI. Copies from assets/generated/svg/dressup/ to the frontend
    serving directory.

    Returns:
        List of destination Path objects for each copied file.
    """
    src_dir = GENERATED_SVG_DIR / "dressup"
    dst_dir = FRONTEND_SVG_DIR / "dressup"
    dst_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if not src_dir.exists():
        return results

    for svg_file in sorted(src_dir.glob("*.svg")):
        dst = dst_dir / svg_file.name
        shutil.copy2(svg_file, dst)
        results.append(dst)

    return results


def copy_mermaid_to_frontend(assembled_path: Path) -> Path:
    """Copy assembled mermaid.svg to frontend/assets/svg/mermaid.svg.

    Args:
        assembled_path: Path to the assembled mermaid.svg.

    Returns:
        Destination Path.
    """
    dst = FRONTEND_SVG_DIR / "mermaid.svg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(assembled_path, dst)
    print(f"  Copied: {assembled_path.name} -> {dst}")
    return dst
