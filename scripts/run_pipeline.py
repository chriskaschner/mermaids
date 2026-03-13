"""Full art pipeline orchestrator -- runs all stages in sequence.

Executes the complete mermaid art generation pipeline:
1. Generate coloring page PNGs (via OpenAI gpt-image-1)
2. Generate 9 dress-up character PNGs (via generate API)
3. Trace coloring pages to SVG (binary mode)
4. Trace dress-up characters to SVG (full color mode)
5. Assemble character SVGs (strip bg, add id)
6. Copy coloring SVGs to frontend
7. Deploy character SVGs to frontend

Each stage is idempotent: re-running skips already-generated files.

Usage:
    uv run python scripts/run_pipeline.py          # full pipeline
    uv run python scripts/run_pipeline.py dressup   # dress-up only

Requires:
    OPENAI_API_KEY environment variable set.
"""

import sys
from pathlib import Path

from mermaids.pipeline.assemble import (
    assemble_combo_svg,
    copy_coloring_pages_to_frontend,
    deploy_characters_to_frontend,
)
from mermaids.pipeline.config import GENERATED_SVG_DIR
from mermaids.pipeline.generate import generate_coloring_pages, generate_dressup_characters

# Allow importing sibling scripts when run as `python scripts/run_pipeline.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))

from trace_all import trace_coloring_pages, trace_dressup_characters


def run_dressup_pipeline():
    """Execute dress-up character pipeline stages."""

    # Stage 1: Generate 9 character PNGs
    print("=" * 60)
    print("STAGE 1: Generate dress-up characters")
    print("=" * 60)
    character_pngs = generate_dressup_characters()
    print(f"  Result: {len(character_pngs)} character PNG(s)\n")

    # Stage 2: Trace characters to SVG
    print("=" * 60)
    print("STAGE 2: Trace characters to SVG")
    print("=" * 60)
    character_svgs = trace_dressup_characters()
    print(f"  Result: {len(character_svgs)} character SVG(s)\n")

    # Stage 3: Assemble each traced SVG (strip bg, add id)
    print("=" * 60)
    print("STAGE 3: Assemble character SVGs")
    print("=" * 60)
    traced_dir = GENERATED_SVG_DIR / "dressup"
    assembled_dir = GENERATED_SVG_DIR / "dressup" / "assembled"
    assembled_dir.mkdir(parents=True, exist_ok=True)

    assembled = []
    for svg_file in sorted(traced_dir.glob("mermaid-*.svg")):
        out = assembled_dir / svg_file.name
        assemble_combo_svg(svg_file, out)
        assembled.append(out)
        print(f"  Assembled: {svg_file.name}")
    print(f"  Result: {len(assembled)} assembled SVG(s)\n")

    # Stage 4: Deploy to frontend
    print("=" * 60)
    print("STAGE 4: Deploy characters to frontend")
    print("=" * 60)
    mermaid_dst = deploy_characters_to_frontend(assembled_dir)
    print(f"  Result: {mermaid_dst}\n")

    return character_pngs, character_svgs, assembled


def run_full_pipeline():
    """Execute all pipeline stages in sequence."""

    # Coloring pages
    print("=" * 60)
    print("COLORING: Generate coloring pages")
    print("=" * 60)
    coloring_pngs = generate_coloring_pages()
    print(f"  Result: {len(coloring_pngs)} coloring page PNG(s)\n")

    print("=" * 60)
    print("COLORING: Trace coloring pages")
    print("=" * 60)
    coloring_svgs = trace_coloring_pages()
    print(f"  Result: {len(coloring_svgs)} coloring SVG(s)\n")

    print("=" * 60)
    print("COLORING: Copy to frontend")
    print("=" * 60)
    copied_coloring = copy_coloring_pages_to_frontend()
    print(f"  Result: {len(copied_coloring)} SVG(s) copied\n")

    # Dress-up characters
    character_pngs, character_svgs, assembled = run_dressup_pipeline()

    # Summary
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Coloring: {len(coloring_pngs)} PNG -> {len(coloring_svgs)} SVG -> {len(copied_coloring)} frontend")
    print(f"  Characters: {len(character_pngs)} PNG -> {len(character_svgs)} SVG -> {len(assembled)} assembled")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "dressup":
        run_dressup_pipeline()
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()
