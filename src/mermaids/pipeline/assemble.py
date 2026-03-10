"""SVG assembly combining traced parts into defs+use mermaid.svg.

Builds a new mermaid.svg with the defs+use structure that the existing
frontend dressup.js expects. Also provides copy utilities for deploying
generated SVGs to the frontend assets directory.
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

# Scale factors: traced SVGs are 1024x1024, target viewBox is 400x700
SCALE_X = 400 / 1024
SCALE_Y = 700 / 1024


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

    Applies a scaling transform to fit the 400x700 viewBox.
    Strips the vtracer background rectangle (first near-white path covering
    the full canvas) to prevent solid color blocks when recoloring.
    """
    g = ET.SubElement(ET.Element("temp"), "g")
    g = ET.Element(f"{{{SVG_NS}}}g")
    g.set("id", variant_id)

    # Add scaling transform (traced at 1024x1024, target is 400x700)
    g.set("transform", f"scale({SCALE_X:.4f}, {SCALE_Y:.4f})")

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


def _make_acc_none() -> ET.Element:
    """Create the acc-none group with invisible hit-area rect."""
    g = ET.Element(f"{{{SVG_NS}}}g")
    g.set("id", "acc-none")

    rect = ET.SubElement(g, f"{{{SVG_NS}}}rect")
    rect.set("x", "170")
    rect.set("y", "20")
    rect.set("width", "60")
    rect.set("height", "40")
    rect.set("fill", "none")
    rect.set("stroke", "none")

    return g


def _make_body_group() -> ET.Element:
    """Create the body group (non-variant torso, arms, shell top).

    These elements are copied from the existing mermaid.svg body region.
    They don't vary between dress-up combinations.
    """
    g = ET.Element(f"{{{SVG_NS}}}g")
    g.set("data-region", "body")
    g.set("pointer-events", "all")

    # Invisible hit-area rect
    rect = ET.SubElement(g, f"{{{SVG_NS}}}rect")
    rect.set("x", "120")
    rect.set("y", "120")
    rect.set("width", "160")
    rect.set("height", "230")
    rect.set("fill", "none")
    rect.set("stroke", "none")

    # Neck
    neck = ET.SubElement(g, f"{{{SVG_NS}}}path")
    neck.set("d", "M188,115 Q188,130 185,140 L215,140 Q212,130 212,115 Z")
    neck.set("fill", "#f5c8a8")

    # Torso
    torso = ET.SubElement(g, f"{{{SVG_NS}}}path")
    torso.set("d", "M155,140 Q145,170 140,220 Q140,260 150,300 "
              "L155,340 Q175,355 200,358 Q225,355 245,340 "
              "L250,300 Q260,260 260,220 Q255,170 245,140 Z")
    torso.set("fill", "#f5c8a8")

    # Left arm
    left_arm = ET.SubElement(g, f"{{{SVG_NS}}}path")
    left_arm.set("d", "M155,155 Q130,180 120,220 Q118,235 125,240 "
                 "Q132,235 138,215 Q145,190 155,170 Z")
    left_arm.set("fill", "#f5c8a8")

    # Right arm
    right_arm = ET.SubElement(g, f"{{{SVG_NS}}}path")
    right_arm.set("d", "M245,155 Q270,180 280,220 Q282,235 275,240 "
                  "Q268,235 262,215 Q255,190 245,170 Z")
    right_arm.set("fill", "#f5c8a8")

    # Shell top accents
    shell_l = ET.SubElement(g, f"{{{SVG_NS}}}ellipse")
    shell_l.set("cx", "180")
    shell_l.set("cy", "175")
    shell_l.set("rx", "18")
    shell_l.set("ry", "12")
    shell_l.set("fill", "#f0b898")

    shell_r = ET.SubElement(g, f"{{{SVG_NS}}}ellipse")
    shell_r.set("cx", "220")
    shell_r.set("cy", "175")
    shell_r.set("rx", "18")
    shell_r.set("ry", "12")
    shell_r.set("fill", "#f0b898")

    return g


def _make_face_details(parent: ET.Element) -> None:
    """Add face detail elements (eyes, sparkles, smile, cheeks) to parent.

    These are placed outside the watercolor filter group for clarity,
    matching the existing mermaid.svg structure.
    """
    # Eyes
    left_eye = ET.SubElement(parent, f"{{{SVG_NS}}}ellipse")
    left_eye.set("cx", "185")
    left_eye.set("cy", "75")
    left_eye.set("rx", "5")
    left_eye.set("ry", "6")
    left_eye.set("fill", "#4a4a6a")

    right_eye = ET.SubElement(parent, f"{{{SVG_NS}}}ellipse")
    right_eye.set("cx", "215")
    right_eye.set("cy", "75")
    right_eye.set("rx", "5")
    right_eye.set("ry", "6")
    right_eye.set("fill", "#4a4a6a")

    # Eye sparkles
    sparkle_l = ET.SubElement(parent, f"{{{SVG_NS}}}circle")
    sparkle_l.set("cx", "187")
    sparkle_l.set("cy", "73")
    sparkle_l.set("r", "1.5")
    sparkle_l.set("fill", "white")

    sparkle_r = ET.SubElement(parent, f"{{{SVG_NS}}}circle")
    sparkle_r.set("cx", "217")
    sparkle_r.set("cy", "73")
    sparkle_r.set("r", "1.5")
    sparkle_r.set("fill", "white")

    # Happy smile
    smile = ET.SubElement(parent, f"{{{SVG_NS}}}path")
    smile.set("d", "M190,90 Q200,100 210,90")
    smile.set("fill", "none")
    smile.set("stroke", "#d4838b")
    smile.set("stroke-width", "2")
    smile.set("stroke-linecap", "round")

    # Rosy cheeks
    cheek_l = ET.SubElement(parent, f"{{{SVG_NS}}}circle")
    cheek_l.set("cx", "175")
    cheek_l.set("cy", "88")
    cheek_l.set("r", "6")
    cheek_l.set("fill", "#f5c0c0")
    cheek_l.set("opacity", "0.5")

    cheek_r = ET.SubElement(parent, f"{{{SVG_NS}}}circle")
    cheek_r.set("cx", "225")
    cheek_r.set("cy", "88")
    cheek_r.set("r", "6")
    cheek_r.set("fill", "#f5c0c0")
    cheek_r.set("opacity", "0.5")


def _make_use(parent: ET.Element, use_id: str, href: str, data_region: str) -> ET.Element:
    """Create a <use> element referencing a defs group."""
    use = ET.SubElement(parent, f"{{{SVG_NS}}}use")
    use.set("id", use_id)
    use.set("href", href)
    use.set("data-region", data_region)
    use.set("pointer-events", "all")
    return use


def assemble_mermaid_svg(traced_parts_dir: Path, output_path: Path) -> Path:
    """Build a mermaid.svg with defs+use structure from traced part SVGs.

    The assembled SVG matches the structure expected by frontend dressup.js:
    - <defs> containing variant groups (tail-1..3, hair-1..3, acc-none, acc-1..3)
    - <use> elements referencing default variants
    - Body group with non-swappable torso/arms/shell
    - Face details outside the main rendering group

    Args:
        traced_parts_dir: Directory containing traced SVGs (tail-1.svg, etc.)
        output_path: Where to write the assembled mermaid.svg.

    Returns:
        The output_path as a Path object.
    """
    output_path = Path(output_path)

    # Create root SVG
    root = ET.Element(f"{{{SVG_NS}}}svg")
    root.set("viewBox", "0 0 400 700")
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

    # Add acc-none (empty group with hit-area)
    defs.append(_make_acc_none())

    # Main rendering group (kawaii style -- no watercolor filter)
    render_group = ET.SubElement(root, f"{{{SVG_NS}}}g")

    # Tail (bottom layer)
    _make_use(render_group, "active-tail", "#tail-1", "tail")

    # Body (middle layer, not swappable)
    render_group.append(_make_body_group())

    # Hair (above body)
    _make_use(render_group, "active-hair", "#hair-1", "hair")

    # Accessory (top layer)
    _make_use(render_group, "active-acc", "#acc-none", "accessory")

    # Face details outside render group for clarity
    _make_face_details(root)

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
