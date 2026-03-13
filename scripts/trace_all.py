"""Trace generated PNGs to SVG line art via vtracer.

Processes coloring page PNGs (binary/outline mode) and dress-up part
PNGs (color mode). Skips files where the output SVG already exists.

Usage:
    uv run python scripts/trace_all.py
"""

from pathlib import Path

from mermaids.pipeline.config import GENERATED_PNG_DIR, GENERATED_SVG_DIR
from mermaids.pipeline.trace import trace_to_svg


def trace_coloring_pages() -> list[Path]:
    """Trace all coloring page PNGs to SVGs with simplify=True (binary mode).

    Scans GENERATED_PNG_DIR/coloring/ for .png files and traces each to
    GENERATED_SVG_DIR/coloring/<same_name>.svg. Skips if the output SVG
    already exists.

    Returns:
        List of output SVG Path objects.
    """
    png_dir = GENERATED_PNG_DIR / "coloring"
    svg_dir = GENERATED_SVG_DIR / "coloring"
    svg_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if not png_dir.exists():
        print(f"  No coloring PNGs found in {png_dir}")
        return results

    for png_file in sorted(png_dir.glob("*.png")):
        svg_out = svg_dir / f"{png_file.stem}.svg"

        if svg_out.exists():
            print(f"  Skip (exists): {svg_out.name}")
            results.append(svg_out)
            continue

        print(f"  Tracing: {png_file.name} -> {svg_out.name}")
        trace_to_svg(png_file, svg_out, simplify=True)
        results.append(svg_out)

    return results


def trace_dressup_characters() -> list[Path]:
    """Trace dress-up character PNGs to SVGs with simplify=False (full color).

    Scans GENERATED_PNG_DIR/dressup/ for mermaid-*.png files and traces each
    to GENERATED_SVG_DIR/dressup/<same_name>.svg. Skips if output exists.

    Returns:
        List of output SVG Path objects.
    """
    png_dir = GENERATED_PNG_DIR / "dressup"
    svg_dir = GENERATED_SVG_DIR / "dressup"
    svg_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if not png_dir.exists():
        print(f"  No dress-up PNGs found in {png_dir}")
        return results

    for png_file in sorted(png_dir.glob("mermaid-*.png")):
        svg_out = svg_dir / f"{png_file.stem}.svg"

        if svg_out.exists():
            print(f"  Skip (exists): {svg_out.name}")
            results.append(svg_out)
            continue

        print(f"  Tracing: {png_file.name} -> {svg_out.name}")
        trace_to_svg(png_file, svg_out, simplify=False)
        results.append(svg_out)

    return results


def main():
    print("Tracing coloring pages (binary/outline mode)...")
    coloring = trace_coloring_pages()
    print(f"  Coloring pages: {len(coloring)} processed")

    print("\nTracing dress-up characters (full color mode)...")
    dressup = trace_dressup_characters()
    print(f"  Dress-up characters: {len(dressup)} processed")

    print(f"\nDone: {len(coloring) + len(dressup)} total SVGs.")


if __name__ == "__main__":
    main()
