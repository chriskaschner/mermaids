"""Assemble traced SVG parts into defs+use mermaid.svg and copy to frontend.

Thin CLI entry point for SVG assembly and frontend asset deployment.

Usage:
    uv run python scripts/assemble_mermaid.py
"""

from mermaids.pipeline.assemble import (
    assemble_mermaid_svg,
    copy_coloring_pages_to_frontend,
    copy_mermaid_to_frontend,
)
from mermaids.pipeline.config import GENERATED_SVG_DIR


def main():
    traced_dir = GENERATED_SVG_DIR / "dressup"
    output = GENERATED_SVG_DIR / "mermaid.svg"

    print("Assembling mermaid.svg from traced parts...")
    assemble_mermaid_svg(traced_dir, output)

    print("\nCopying coloring pages to frontend...")
    coloring = copy_coloring_pages_to_frontend()
    print(f"  {len(coloring)} coloring page(s) copied")

    print("\nCopying mermaid.svg to frontend...")
    copy_mermaid_to_frontend(output)

    print("\nDone.")


if __name__ == "__main__":
    main()
