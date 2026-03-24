"""Generate B&W coloring outline SVGs for all 9 dress-up characters.

Uses the existing AI pipeline pattern:
  COLORING_BASE_PROMPT + DRESSUP_CHARACTERS[i]['prompt_detail']
  → generate PNG via gpt-image-1
  → trace to SVG via vtracer
  → save to frontend/assets/svg/dressup-coloring/{character['id']}-outline.svg

If OPENAI_API_KEY is not set, exits with a clear error message.
Use --dry-run to preview what would be generated without calling the API.
Use --placeholder to create simple geometric placeholder SVGs instead (no API needed).

Usage:
    uv run python scripts/generate_dressup_outlines.py
    uv run python scripts/generate_dressup_outlines.py --dry-run
    uv run python scripts/generate_dressup_outlines.py --placeholder
"""

import argparse
import os
import sys
import textwrap
from pathlib import Path

# Ensure the src package is importable when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mermaids.pipeline.config import FRONTEND_SVG_DIR, GENERATED_PNG_DIR
from mermaids.pipeline.prompts import COLORING_BASE_PROMPT, DRESSUP_CHARACTERS

OUTPUT_DIR = FRONTEND_SVG_DIR / "dressup-coloring"

# ---------------------------------------------------------------------------
# Placeholder SVG generation (no API key needed)
# ---------------------------------------------------------------------------

# Per-character distinctive shapes so each placeholder looks different.
# Each entry: (hair_path_d, tail_path_d, hair_label)
_CHARACTER_SHAPES = {
    "mermaid-1": {
        # Long wavy hair, rounded fins
        "hair": "M 340,80 Q 300,120 290,200 Q 280,280 300,330 Q 380,300 420,200 Q 440,140 400,80 Z",
        "tail": "M 340,600 Q 280,650 260,720 Q 300,780 370,800 Q 430,800 460,720 Q 440,650 380,600 Z",
        "fin_l": "M 260,720 Q 200,750 190,790 Q 220,800 260,780",
        "fin_r": "M 460,720 Q 520,750 530,790 Q 500,800 460,780",
        "accessory": '<circle cx="370" cy="480" r="8" fill="none" stroke="#000" stroke-width="3"/>'
            '<circle cx="355" cy="490" r="8" fill="none" stroke="#000" stroke-width="3"/>'
            '<circle cx="385" cy="490" r="8" fill="none" stroke="#000" stroke-width="3"/>',
    },
    "mermaid-2": {
        # Twin pigtails with bows
        "hair": "M 310,80 Q 270,100 260,150 Q 250,190 270,210 Q 310,190 320,150 Z"
               " M 430,80 Q 470,100 480,150 Q 490,190 470,210 Q 430,190 420,150 Z"
               " M 310,80 L 430,80 Q 390,110 370,120 Q 350,110 310,80 Z",
        "tail": "M 340,600 Q 270,660 250,730 Q 300,790 370,800 Q 440,800 480,730 Q 460,660 400,600 Z",
        "fin_l": "M 250,730 Q 200,770 200,800 Q 230,800 260,780",
        "fin_r": "M 480,730 Q 530,770 540,800 Q 510,800 480,780",
        "accessory": '<path d="M 280,190 Q 265,200 260,195 Q 265,185 280,190 Z" fill="none" stroke="#000" stroke-width="3"/>'
            '<path d="M 460,190 Q 475,200 480,195 Q 475,185 460,190 Z" fill="none" stroke="#000" stroke-width="3"/>',
    },
    "mermaid-3": {
        # Long curly hair, scalloped tail
        "hair": "M 300,80 Q 260,130 250,200 Q 240,260 255,320 Q 310,300 330,230 Q 350,160 330,80 Z"
               " M 420,80 Q 450,150 440,230 Q 430,300 410,320 Q 400,220 410,140 Z",
        "tail": "M 340,600 Q 280,640 260,710 Q 300,760 370,780 Q 440,760 480,710 Q 460,640 400,600 Z"
               " M 310,680 Q 290,700 295,720 M 370,670 Q 360,695 365,715 M 430,680 Q 450,700 445,720",
        "fin_l": "M 260,710 Q 210,750 205,790 Q 240,800 265,775",
        "fin_r": "M 480,710 Q 530,750 535,790 Q 500,800 475,775",
        "accessory": '<path d="M 350,430 Q 370,440 390,430 Q 380,450 370,455 Q 360,450 350,430 Z" fill="none" stroke="#000" stroke-width="3"/>',
    },
    "mermaid-4": {
        # Straight hair in a braid, fan-shaped fin
        "hair": "M 340,80 L 330,320 Q 360,330 390,320 L 380,80 Z"
               " M 340,80 Q 360,90 380,80",
        "tail": "M 340,600 Q 290,650 275,720 Q 310,780 370,795 Q 430,780 465,720 Q 450,650 400,600 Z",
        "fin_l": "M 275,720 Q 220,745 215,785 Q 250,790 278,760",
        "fin_r": "M 465,720 Q 520,745 525,785 Q 490,790 462,760",
        "accessory": '<path d="M 330,430 Q 370,415 410,430 Q 390,420 370,418 Q 350,420 330,430 Z" fill="none" stroke="#000" stroke-width="3"/>',
    },
    "mermaid-5": {
        # Afro puffs — two round hair shapes
        "hair": "M 290,120 Q 250,100 240,140 Q 230,180 260,200 Q 300,210 320,180 Q 330,150 310,120 Z"
               " M 450,120 Q 490,100 500,140 Q 510,180 480,200 Q 440,210 420,180 Q 410,150 430,120 Z",
        "tail": "M 340,600 Q 285,645 268,715 Q 305,775 370,790 Q 435,775 472,715 Q 455,645 400,600 Z",
        "fin_l": "M 268,715 Q 215,748 212,788 Q 245,795 270,768",
        "fin_r": "M 472,715 Q 525,748 528,788 Q 495,795 470,768",
        "accessory": '<circle cx="345" cy="520" r="15" fill="none" stroke="#000" stroke-width="3"/>'
            '<line x1="345" y1="505" x2="345" y2="490" stroke="#000" stroke-width="3"/>',
    },
    "mermaid-6": {
        # Long braids with beads
        "hair": "M 315,80 Q 285,150 278,250 Q 272,330 285,370 Q 325,340 330,250 Q 340,160 330,80 Z"
               " M 425,80 Q 455,150 462,250 Q 468,330 455,370 Q 415,340 410,250 Q 400,160 410,80 Z",
        "tail": "M 340,600 Q 282,648 265,718 Q 303,778 370,793 Q 437,778 475,718 Q 458,648 400,600 Z",
        "fin_l": "M 265,718 Q 212,750 208,790 Q 242,797 268,770",
        "fin_r": "M 475,718 Q 528,750 532,790 Q 498,797 472,770",
        "accessory": '<circle cx="300" cy="240" r="5" fill="#000" stroke="#000" stroke-width="2"/>'
            '<circle cx="440" cy="240" r="5" fill="#000" stroke="#000" stroke-width="2"/>',
    },
    "mermaid-7": {
        # Coily hair with a flower
        "hair": "M 310,100 Q 265,120 255,175 Q 248,225 268,262 Q 310,248 330,200 Q 345,155 325,100 Z"
               " M 430,100 Q 475,120 485,175 Q 492,225 472,262 Q 430,248 410,200 Q 395,155 415,100 Z"
               " M 310,100 Q 370,80 430,100",
        "tail": "M 340,600 Q 276,652 258,724 Q 297,782 370,796 Q 443,782 482,724 Q 464,652 400,600 Z",
        "fin_l": "M 258,724 Q 202,759 199,797 Q 234,802 261,774",
        "fin_r": "M 482,724 Q 538,759 541,797 Q 506,802 479,774",
        "accessory": '<circle cx="330" cy="105" r="12" fill="none" stroke="#000" stroke-width="3"/>'
            '<circle cx="330" cy="105" r="5" fill="none" stroke="#000" stroke-width="2"/>',
    },
    "mermaid-8": {
        # Locs with tips
        "hair": "M 305,80 Q 268,130 260,200 Q 254,262 268,312 Q 310,290 325,225 Q 338,158 322,80 Z"
               " M 435,80 Q 472,130 480,200 Q 486,262 472,312 Q 430,290 415,225 Q 402,158 418,80 Z",
        "tail": "M 340,600 Q 278,654 260,726 Q 299,784 370,798 Q 441,784 480,726 Q 462,654 400,600 Z",
        "fin_l": "M 260,726 Q 204,761 201,799 Q 236,804 263,776",
        "fin_r": "M 480,726 Q 536,761 539,799 Q 504,804 477,776",
        "accessory": '<path d="M 268,250 Q 262,260 268,270 Q 276,270 278,260 Z" fill="none" stroke="#000" stroke-width="2"/>'
            '<path d="M 472,250 Q 478,260 472,270 Q 464,270 462,260 Z" fill="none" stroke="#000" stroke-width="2"/>',
    },
    "mermaid-9": {
        # Short mint bob with bangs
        "hair": "M 310,110 Q 280,130 275,165 Q 280,200 310,210 Q 340,215 370,215 Q 400,215 430,210 Q 460,200 465,165 Q 460,130 430,110 Z"
               " M 310,110 Q 340,95 370,93 Q 400,95 430,110",
        "tail": "M 335,600 Q 272,655 253,728 Q 293,786 370,800 Q 447,786 487,728 Q 468,655 405,600 Z",
        "fin_l": "M 253,728 Q 196,764 193,802 Q 228,807 256,778",
        "fin_r": "M 487,728 Q 544,764 547,802 Q 512,807 484,778",
        "accessory": '<path d="M 380,213 Q 390,205 395,213 Q 390,220 380,213 Z" fill="none" stroke="#000" stroke-width="2"/>',
    },
}


def _build_placeholder_svg(char_id: str) -> str:
    """Build a standalone B&W mermaid outline SVG for a given character ID.

    The SVG is 1024x1024 with a white background and black outlines only —
    no fills — so it is a valid coloring target for flood-fill on a canvas.

    Shapes are distinct per character so they are visually identifiable.
    """
    shapes = _CHARACTER_SHAPES[char_id]
    char_num = char_id.replace("mermaid-", "")

    hair_d = shapes["hair"]
    tail_d = shapes["tail"]
    fin_l = shapes["fin_l"]
    fin_r = shapes["fin_r"]
    accessory = shapes.get("accessory", "")

    return textwrap.dedent(f"""\
        <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
             width="1024" height="1024" viewBox="0 0 1024 1024">
          <!-- BandW outline placeholder for dress-up coloring: {char_id} -->
          <!-- Generated by scripts/generate_dressup_outlines.py -placeholder -->
          <rect width="1024" height="1024" fill="white"/>

          <!-- Head -->
          <ellipse cx="370" cy="300" rx="100" ry="110"
                   fill="white" stroke="#000" stroke-width="3"/>

          <!-- Eyes -->
          <ellipse cx="340" cy="290" rx="18" ry="20"
                   fill="white" stroke="#000" stroke-width="3"/>
          <ellipse cx="400" cy="290" rx="18" ry="20"
                   fill="white" stroke="#000" stroke-width="3"/>
          <circle  cx="340" cy="292" r="9" fill="#000"/>
          <circle  cx="400" cy="292" r="9" fill="#000"/>
          <circle  cx="344" cy="287" r="3" fill="white"/>
          <circle  cx="404" cy="287" r="3" fill="white"/>

          <!-- Nose -->
          <path d="M 366,315 Q 370,320 374,315" fill="none" stroke="#000" stroke-width="2"/>

          <!-- Mouth -->
          <path d="M 354,330 Q 370,342 386,330" fill="none" stroke="#000" stroke-width="2.5"/>

          <!-- Hair -->
          <path d="{hair_d}"
                fill="white" stroke="#000" stroke-width="3"
                stroke-linejoin="round"/>

          <!-- Body torso -->
          <path d="M 280,390 Q 260,450 265,530 L 340,535 L 340,390 Z"
                fill="white" stroke="#000" stroke-width="3"/>
          <path d="M 460,390 Q 480,450 475,530 L 400,535 L 400,390 Z"
                fill="white" stroke="#000" stroke-width="3"/>
          <path d="M 280,390 Q 295,370 340,365 L 400,365 Q 445,370 460,390"
                fill="white" stroke="#000" stroke-width="3"/>
          <rect x="340" y="365" width="60" height="170"
                fill="white" stroke="#000" stroke-width="3" rx="2"/>

          <!-- Waist band -->
          <path d="M 265,530 Q 310,550 370,555 Q 430,550 475,530 L 400,535 L 340,535 Z"
                fill="white" stroke="#000" stroke-width="3"/>

          <!-- Tail -->
          <path d="{tail_d}"
                fill="white" stroke="#000" stroke-width="3"
                stroke-linejoin="round"/>

          <!-- Fins -->
          <path d="{fin_l}"
                fill="white" stroke="#000" stroke-width="3"/>
          <path d="{fin_r}"
                fill="white" stroke="#000" stroke-width="3"/>

          <!-- Arms -->
          <path d="M 265,420 Q 220,460 215,510 Q 235,525 255,500 Q 265,460 280,435"
                fill="white" stroke="#000" stroke-width="3"/>
          <path d="M 475,420 Q 520,460 525,510 Q 505,525 485,500 Q 475,460 460,435"
                fill="white" stroke="#000" stroke-width="3"/>

          <!-- Hands -->
          <ellipse cx="222" cy="518" rx="18" ry="14"
                   fill="white" stroke="#000" stroke-width="3"/>
          <ellipse cx="518" cy="518" rx="18" ry="14"
                   fill="white" stroke="#000" stroke-width="3"/>

          <!-- Character-specific accessory -->
          {accessory}

          <!-- Label character number -->
          <text x="512" y="1005" font-family="sans-serif" font-size="28"
                text-anchor="middle" fill="#aaa">{char_num}</text>
        </svg>
    """)


def generate_placeholders(output_dir: Path) -> list[Path]:
    """Write placeholder B&W outline SVGs for all 9 dress-up characters."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for char in DRESSUP_CHARACTERS:
        out = output_dir / f"{char['id']}-outline.svg"
        if out.exists():
            print(f"  Skip (exists): {out.name}")
            results.append(out)
            continue
        svg_content = _build_placeholder_svg(char["id"])
        out.write_text(svg_content, encoding="utf-8")
        size = out.stat().st_size
        print(f"  Created placeholder: {out.name}  ({size:,} bytes)")
        results.append(out)
    return results


def generate_ai_outlines(output_dir: Path, dry_run: bool = False) -> list[Path]:
    """Generate B&W outline SVGs via the AI pipeline (requires OPENAI_API_KEY).

    In dry-run mode, only prints what would be generated without any API call.
    Raises EnvironmentError if OPENAI_API_KEY is not set (unless dry_run=True).
    """
    if not dry_run:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. "
                "Set the env var to generate outlines via the AI pipeline, "
                "or use --placeholder to create simple geometric placeholders."
            )

    from mermaids.pipeline.generate import generate_image
    from mermaids.pipeline.trace import trace_to_svg

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_png_dir = GENERATED_PNG_DIR / "dressup-coloring"
    tmp_png_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for char in DRESSUP_CHARACTERS:
        prompt = COLORING_BASE_PROMPT + char["prompt_detail"]
        out_svg = output_dir / f"{char['id']}-outline.svg"

        if dry_run:
            print(f"  [dry-run] Would generate: {out_svg.name}")
            print(f"            Prompt: {prompt[:80]}...")
            results.append(out_svg)
            continue

        if out_svg.exists():
            print(f"  Skip (exists): {out_svg.name}")
            results.append(out_svg)
            continue

        print(f"  Generating PNG: {char['id']} ...")
        png_path = tmp_png_dir / f"{char['id']}-outline.png"
        generate_image(prompt, png_path, quality="high")

        print(f"  Tracing to SVG: {out_svg.name} ...")
        trace_to_svg(png_path, out_svg, simplify=True)
        size = out_svg.stat().st_size
        print(f"  Done: {out_svg.name}  ({size:,} bytes)")
        results.append(out_svg)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate B&W coloring outline SVGs for all 9 dress-up characters."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without calling the OpenAI API.",
    )
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help=(
            "Create simple geometric placeholder SVGs instead of calling the API. "
            "Useful when OPENAI_API_KEY is not available."
        ),
    )
    args = parser.parse_args()

    output_dir = OUTPUT_DIR
    print(f"Output directory: {output_dir}")

    if args.placeholder:
        print("Creating placeholder SVGs (no API call)...")
        results = generate_placeholders(output_dir)
        print(f"\nDone: {len(results)} placeholder SVG(s) written.")
    else:
        if args.dry_run:
            print("Dry-run mode — no API calls will be made.")
            generate_ai_outlines(output_dir, dry_run=True)
        else:
            print("Generating via AI pipeline (requires OPENAI_API_KEY)...")
            try:
                results = generate_ai_outlines(output_dir, dry_run=False)
                print(f"\nDone: {len(results)} outline SVG(s) generated.")
            except EnvironmentError as exc:
                print(f"\nError: {exc}", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
