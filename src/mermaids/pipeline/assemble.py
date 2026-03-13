"""SVG assembly for composite dress-up characters.

Each composite is a single pre-built character (one combination of hair, eyes,
tail, accessories). The frontend swaps the entire SVG when the user changes any
part, rather than swapping individual layers.

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

# Expected variant part IDs in order (12 total: 3 per category)
VARIANT_IDS = [
    "tail-1", "tail-2", "tail-3",
    "hair-1", "hair-2", "hair-3",
    "eye-1",  "eye-2",  "eye-3",
    "acc-1",  "acc-2",  "acc-3",
]

# ID for the static base body group in defs
BODY_ID = "body"

# Default combo indices (all variant 1)
DEFAULT_COMBO = "combo-1-1-1-1"


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


def assemble_combo_svg(traced_svg_path: Path, output_path: Path) -> Path:
    """Build a mermaid SVG from a single traced composite image.

    Takes a traced SVG (from a pre-composited PNG) and wraps it in
    the expected structure with id="mermaid-svg". Strips the vtracer
    background rectangle.

    Args:
        traced_svg_path: Path to the traced composite SVG.
        output_path: Where to write the assembled SVG.

    Returns:
        The output_path as a Path object.
    """
    output_path = Path(output_path)

    root = ET.Element(f"{{{SVG_NS}}}svg")
    root.set("viewBox", "0 0 1024 1024")
    root.set("preserveAspectRatio", "xMidYMid meet")
    root.set("id", "mermaid-svg")

    try:
        tree = ET.parse(traced_svg_path)
        src_root = tree.getroot()

        first_child = True
        for child in src_root:
            if first_child and _is_background_path(child):
                first_child = False
                continue
            first_child = False
            root.append(child)
    except ET.ParseError:
        pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=False)

    return output_path


def assemble_all_combos(traced_combos_dir: Path, output_dir: Path) -> list[Path]:
    """Assemble all traced composite SVGs into frontend-ready SVGs.

    Args:
        traced_combos_dir: Directory with traced combo SVGs (combo-1-1-1-1.svg, etc.)
        output_dir: Where to write assembled SVGs.

    Returns:
        List of output paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for svg_file in sorted(traced_combos_dir.glob("combo-*.svg")):
        output = output_dir / svg_file.name
        assemble_combo_svg(svg_file, output)
        results.append(output)

    print(f"  Assembled {len(results)} combo SVGs")
    return results


def deploy_combos_to_frontend(assembled_dir: Path) -> Path:
    """Copy assembled combo SVGs to frontend and set the default mermaid.svg.

    Copies all combo SVGs to frontend/assets/svg/dressup/.
    Copies the default combo (1-1-1-1) as mermaid.svg.

    Args:
        assembled_dir: Directory containing assembled combo SVGs.

    Returns:
        Path to the default mermaid.svg in the frontend.
    """
    dst_dir = FRONTEND_SVG_DIR / "dressup"
    dst_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for svg_file in sorted(assembled_dir.glob("combo-*.svg")):
        dst = dst_dir / svg_file.name
        shutil.copy2(svg_file, dst)
        count += 1

    # Copy default combo as mermaid.svg
    default_src = assembled_dir / f"{DEFAULT_COMBO}.svg"
    mermaid_dst = FRONTEND_SVG_DIR / "mermaid.svg"
    if default_src.exists():
        shutil.copy2(default_src, mermaid_dst)

    print(f"  Deployed {count} combo SVGs + mermaid.svg to frontend")
    return mermaid_dst


def deploy_characters_to_frontend(assembled_dir: Path) -> Path:
    """Deploy assembled mermaid character SVGs to the frontend.

    Copies mermaid-{1..9}.svg to frontend/assets/svg/dressup/.
    Copies mermaid-1.svg as the default mermaid.svg.

    Args:
        assembled_dir: Directory containing assembled mermaid-*.svg files.

    Returns:
        Path to the default mermaid.svg in the frontend.
    """
    dst_dir = FRONTEND_SVG_DIR / "dressup"
    dst_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for svg_file in sorted(assembled_dir.glob("mermaid-*.svg")):
        dst = dst_dir / svg_file.name
        shutil.copy2(svg_file, dst)
        count += 1

    # Copy mermaid-1 as the default mermaid.svg
    default_src = assembled_dir / "mermaid-1.svg"
    mermaid_dst = FRONTEND_SVG_DIR / "mermaid.svg"
    if default_src.exists():
        shutil.copy2(default_src, mermaid_dst)

    print(f"  Deployed {count} character SVGs + mermaid.svg to frontend")
    return mermaid_dst


# --- Legacy functions kept for coloring page support ---


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
