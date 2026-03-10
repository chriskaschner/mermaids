"""Full art pipeline orchestrator -- runs all stages in sequence.

Executes the complete mermaid art generation pipeline:
1. Generate coloring page PNGs (via OpenAI gpt-image-1)
2. Generate dress-up base + 9 variant PNGs (via edit API)
3. Trace coloring pages to SVG (binary mode)
4. Trace dress-up parts to SVG (color mode)
5. Assemble traced parts into mermaid.svg (defs+use structure)
6. Copy coloring SVGs to frontend
7. Copy mermaid.svg to frontend

Each stage is idempotent: re-running skips already-generated files.

Usage:
    uv run python scripts/run_pipeline.py

Requires:
    OPENAI_API_KEY environment variable set.
"""

from mermaids.pipeline.assemble import (
    assemble_mermaid_svg,
    copy_coloring_pages_to_frontend,
    copy_mermaid_to_frontend,
)
from mermaids.pipeline.config import GENERATED_SVG_DIR
from mermaids.pipeline.edit import generate_dressup_variants
from mermaids.pipeline.generate import generate_coloring_pages
import sys
from pathlib import Path

# Allow importing sibling scripts when run as `python scripts/run_pipeline.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))

from trace_all import trace_coloring_pages, trace_dressup_parts


def run_full_pipeline():
    """Execute all pipeline stages in sequence."""

    # Stage 1: Generate coloring page PNGs
    print("=" * 60)
    print("STAGE 1: Generate coloring pages")
    print("=" * 60)
    coloring_pngs = generate_coloring_pages()
    print(f"  Result: {len(coloring_pngs)} coloring page PNG(s)\n")

    # Stage 2: Generate dress-up base + variant PNGs
    print("=" * 60)
    print("STAGE 2: Generate dress-up variants")
    print("=" * 60)
    dressup_pngs = generate_dressup_variants()
    print(f"  Result: {len(dressup_pngs)} dress-up variant PNG(s)\n")

    # Stage 3: Trace coloring pages to SVG
    print("=" * 60)
    print("STAGE 3: Trace coloring pages")
    print("=" * 60)
    coloring_svgs = trace_coloring_pages()
    print(f"  Result: {len(coloring_svgs)} coloring SVG(s)\n")

    # Stage 4: Trace dress-up parts to SVG
    print("=" * 60)
    print("STAGE 4: Trace dress-up parts")
    print("=" * 60)
    dressup_svgs = trace_dressup_parts()
    print(f"  Result: {len(dressup_svgs)} dress-up SVG(s)\n")

    # Stage 5: Assemble mermaid.svg
    print("=" * 60)
    print("STAGE 5: Assemble mermaid.svg")
    print("=" * 60)
    traced_dir = GENERATED_SVG_DIR / "dressup"
    assembled = GENERATED_SVG_DIR / "mermaid.svg"
    assemble_mermaid_svg(traced_dir, assembled)
    print(f"  Result: {assembled}\n")

    # Stage 6: Copy coloring SVGs to frontend
    print("=" * 60)
    print("STAGE 6: Copy coloring pages to frontend")
    print("=" * 60)
    copied_coloring = copy_coloring_pages_to_frontend()
    print(f"  Result: {len(copied_coloring)} SVG(s) copied\n")

    # Stage 7: Copy mermaid.svg to frontend
    print("=" * 60)
    print("STAGE 7: Copy mermaid.svg to frontend")
    print("=" * 60)
    copied_mermaid = copy_mermaid_to_frontend(assembled)
    print(f"  Result: {copied_mermaid}\n")

    # Summary
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Coloring pages: {len(coloring_pngs)} PNG -> {len(coloring_svgs)} SVG -> {len(copied_coloring)} frontend")
    print(f"  Dress-up parts: {len(dressup_pngs)} PNG -> {len(dressup_svgs)} SVG -> assembled")
    print(f"  Mermaid SVG: {copied_mermaid}")


def main():
    run_full_pipeline()


if __name__ == "__main__":
    main()
