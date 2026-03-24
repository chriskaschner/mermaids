"""Generate scene-themed B&W coloring placeholder SVGs for pages 5-9.

Pages 5-9 of the coloring gallery were 170-byte empty vtracer stubs.
This script replaces them with 1024x1024 geometric placeholder SVGs using
the same B&W outline pattern as generate_dressup_outlines.py --placeholder.

Each SVG contains a mermaid figure plus scene-specific elements, with
>= 8 <path elements per file (mermaid body paths + scene paths).

Scenes:
  page-5-forest   — kelp forest (tall seaweed stalks, bubbles)
  page-6-treasure — treasure chest on ocean floor (chest, coins, gems)
  page-7-jellyfish — jellyfish meadow (2-3 jellyfish with tentacles)
  page-8-whirlpool — whirlpool vortex (spiral paths, swirling bubbles)
  page-9-starfish  — starfish beach (starfish shapes, sand dollars)

Usage:
    uv run python scripts/generate_coloring_placeholders.py

Output: frontend/assets/svg/coloring/page-{5..9}-*.svg
Observability: prints each file path, size in bytes, and <path count on success.
               prints ERROR to stderr and exits non-zero on any write failure.
"""

import sys
import textwrap
from pathlib import Path

# Ensure the src package is importable when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "assets"
    / "svg"
    / "coloring"
)

# ---------------------------------------------------------------------------
# Shared mermaid body template (reusable across scenes)
# ---------------------------------------------------------------------------

# This builds the core mermaid figure as a list of SVG element strings.
# Each element becomes one <path, <ellipse, or <circle in the final SVG.
# The figure is centered at ~x=512, positioned in upper 2/3 of the frame.
_MERMAID_BODY = """\
  <!-- Mermaid body: head -->
  <ellipse cx="512" cy="260" rx="90" ry="100"
           fill="white" stroke="#000" stroke-width="3"/>
  <!-- Eyes -->
  <ellipse cx="485" cy="252" rx="14" ry="16"
           fill="white" stroke="#000" stroke-width="3"/>
  <ellipse cx="539" cy="252" rx="14" ry="16"
           fill="white" stroke="#000" stroke-width="3"/>
  <circle  cx="485" cy="254" r="7" fill="#000"/>
  <circle  cx="539" cy="254" r="7" fill="#000"/>
  <!-- Nose -->
  <path d="M 508,275 Q 512,281 516,275" fill="none" stroke="#000" stroke-width="2"/>
  <!-- Mouth -->
  <path d="M 498,292 Q 512,303 526,292" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Hair -->
  <path d="M 435,200 Q 400,240 398,320 Q 440,310 450,250 Q 460,210 440,195 Z"
        fill="white" stroke="#000" stroke-width="3" stroke-linejoin="round"/>
  <path d="M 589,200 Q 624,240 626,320 Q 584,310 574,250 Q 564,210 584,195 Z"
        fill="white" stroke="#000" stroke-width="3" stroke-linejoin="round"/>
  <path d="M 435,200 Q 512,180 589,200" fill="none" stroke="#000" stroke-width="3"/>
  <!-- Torso left side -->
  <path d="M 430,348 Q 415,400 418,470 L 487,474 L 487,348 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Torso right side -->
  <path d="M 594,348 Q 609,400 606,470 L 537,474 L 537,348 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Torso center -->
  <rect x="487" y="348" width="50" height="126"
        fill="white" stroke="#000" stroke-width="3" rx="2"/>
  <!-- Waist band -->
  <path d="M 418,470 Q 460,488 512,492 Q 564,488 606,470 L 537,474 L 487,474 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Tail -->
  <path d="M 487,490 Q 445,545 440,620 Q 480,680 512,692 Q 544,680 584,620 Q 579,545 537,490 Z"
        fill="white" stroke="#000" stroke-width="3" stroke-linejoin="round"/>
  <!-- Left fin -->
  <path d="M 440,620 Q 395,655 390,695 Q 418,700 445,675"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Right fin -->
  <path d="M 584,620 Q 629,655 634,695 Q 606,700 579,675"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Left arm -->
  <path d="M 418,378 Q 380,415 376,460 Q 392,472 407,450 Q 416,418 430,398"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Right arm -->
  <path d="M 606,378 Q 644,415 648,460 Q 632,472 617,450 Q 608,418 594,398"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Left hand -->
  <ellipse cx="382" cy="468" rx="15" ry="11"
           fill="white" stroke="#000" stroke-width="3"/>
  <!-- Right hand -->
  <ellipse cx="642" cy="468" rx="15" ry="11"
           fill="white" stroke="#000" stroke-width="3"/>"""


# ---------------------------------------------------------------------------
# Per-scene element definitions
# ---------------------------------------------------------------------------

_SCENE_ELEMENTS = {
    "page-5-forest": """\
  <!-- Scene: Kelp forest -->
  <!-- Kelp stalk 1 -->
  <path d="M 200,1024 Q 210,900 190,780 Q 175,660 205,540 Q 220,420 200,300"
        fill="none" stroke="#000" stroke-width="8" stroke-linecap="round"/>
  <!-- Kelp blade 1a -->
  <path d="M 200,800 Q 160,760 155,720 Q 175,730 200,760"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Kelp blade 1b -->
  <path d="M 200,650 Q 240,620 250,585 Q 228,598 200,625"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Kelp stalk 2 -->
  <path d="M 830,1024 Q 818,880 840,760 Q 858,650 825,530 Q 808,420 835,310"
        fill="none" stroke="#000" stroke-width="8" stroke-linecap="round"/>
  <!-- Kelp blade 2a -->
  <path d="M 830,820 Q 875,785 880,748 Q 858,757 830,785"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Kelp blade 2b -->
  <path d="M 830,660 Q 788,635 778,598 Q 800,610 830,640"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Bubble cluster -->
  <circle cx="280" cy="480" r="12" fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="305" cy="450" r="8"  fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="268" cy="420" r="15" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Second bubble cluster -->
  <circle cx="750" cy="520" r="10" fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="778" cy="490" r="14" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Ocean floor -->
  <path d="M 0,980 Q 256,960 512,968 Q 768,976 1024,960 L 1024,1024 L 0,1024 Z"
        fill="white" stroke="#000" stroke-width="3"/>""",

    "page-6-treasure": """\
  <!-- Scene: Treasure chest on ocean floor -->
  <!-- Chest body -->
  <rect x="340" y="780" width="200" height="140"
        fill="white" stroke="#000" stroke-width="4" rx="6"/>
  <!-- Chest lid -->
  <path d="M 340,780 Q 340,735 440,730 Q 540,735 540,780 Z"
        fill="white" stroke="#000" stroke-width="4"/>
  <!-- Chest hinge band -->
  <rect x="340" y="774" width="200" height="16"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Chest latch -->
  <rect x="424" y="830" width="32" height="24"
        fill="white" stroke="#000" stroke-width="3" rx="3"/>
  <circle cx="440" cy="842" r="6" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Chest corner reinforcements -->
  <path d="M 340,780 L 340,920 M 540,780 L 540,920" fill="none" stroke="#000" stroke-width="3"/>
  <!-- Gold coins spilling out -->
  <ellipse cx="310" cy="915" rx="20" ry="12" fill="none" stroke="#000" stroke-width="2.5"/>
  <ellipse cx="280" cy="930" rx="18" ry="11" fill="none" stroke="#000" stroke-width="2.5"/>
  <ellipse cx="570" cy="910" rx="20" ry="12" fill="none" stroke="#000" stroke-width="2.5"/>
  <ellipse cx="600" cy="928" rx="16" ry="10" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Gem sparkle left -->
  <path d="M 250,850 L 258,840 L 266,850 L 258,860 Z"
        fill="white" stroke="#000" stroke-width="2.5"/>
  <!-- Gem sparkle right -->
  <path d="M 650,855 L 660,842 L 670,855 L 660,868 Z"
        fill="white" stroke="#000" stroke-width="2.5"/>
  <!-- Ocean floor -->
  <path d="M 0,968 Q 256,950 512,958 Q 768,966 1024,950 L 1024,1024 L 0,1024 Z"
        fill="white" stroke="#000" stroke-width="3"/>""",

    "page-7-jellyfish": """\
  <!-- Scene: Jellyfish meadow -->
  <!-- Jellyfish 1 (large, left) -->
  <path d="M 180,200 Q 100,200 90,280 Q 80,360 180,370 Q 280,360 270,280 Q 260,200 180,200 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Jellyfish 1 inner bell detail -->
  <path d="M 130,260 Q 180,240 230,260 Q 220,290 180,295 Q 140,290 130,260 Z"
        fill="white" stroke="#000" stroke-width="2.5"/>
  <!-- Jellyfish 1 tentacles -->
  <path d="M 135,368 Q 128,430 140,510 Q 148,570 135,630"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 165,372 Q 155,450 165,530 Q 172,590 158,660"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 195,372 Q 198,455 192,535 Q 188,595 198,665"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 225,368 Q 235,445 225,525 Q 218,588 230,650"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <!-- Jellyfish 2 (small, right) -->
  <path d="M 800,140 Q 740,140 732,200 Q 724,260 800,268 Q 876,260 868,200 Q 860,140 800,140 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Jellyfish 2 inner bell -->
  <path d="M 762,185 Q 800,172 838,185 Q 830,205 800,208 Q 770,205 762,185 Z"
        fill="white" stroke="#000" stroke-width="2"/>
  <!-- Jellyfish 2 tentacles -->
  <path d="M 762,266 Q 755,320 765,380 Q 772,430 760,490"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 800,270 Q 800,330 800,395 Q 800,448 795,508"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 838,266 Q 845,320 835,380 Q 828,430 840,490"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <!-- Jellyfish 3 (tiny, background) -->
  <path d="M 680,380 Q 648,380 644,412 Q 640,444 680,448 Q 720,444 716,412 Q 712,380 680,380 Z"
        fill="white" stroke="#000" stroke-width="2.5"/>
  <path d="M 660,447 Q 656,478 662,510"
        fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M 680,449 Q 680,482 678,514"
        fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M 700,447 Q 704,478 698,510"
        fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>
  <!-- Bubbles -->
  <circle cx="380" cy="350" r="10" fill="none" stroke="#000" stroke-width="2"/>
  <circle cx="400" cy="318" r="7"  fill="none" stroke="#000" stroke-width="2"/>""",

    "page-8-whirlpool": """\
  <!-- Scene: Whirlpool vortex -->
  <!-- Outer vortex ring 1 -->
  <path d="M 512,100 Q 780,150 880,380 Q 950,560 840,740 Q 720,900 512,920 Q 304,900 184,740 Q 74,560 144,380 Q 244,150 512,100"
        fill="none" stroke="#000" stroke-width="4" stroke-linecap="round"/>
  <!-- Vortex ring 2 -->
  <path d="M 512,180 Q 730,220 808,420 Q 860,575 768,724 Q 672,860 512,876 Q 352,860 256,724 Q 164,575 216,420 Q 294,220 512,180"
        fill="none" stroke="#000" stroke-width="3.5" stroke-linecap="round"/>
  <!-- Vortex ring 3 (tighter) -->
  <path d="M 512,280 Q 680,308 736,460 Q 768,580 700,700 Q 628,808 512,820 Q 396,808 324,700 Q 256,580 288,460 Q 344,308 512,280"
        fill="none" stroke="#000" stroke-width="3" stroke-linecap="round"/>
  <!-- Vortex core (small spiral detail) -->
  <circle cx="512" cy="740" r="30" fill="white" stroke="#000" stroke-width="3"/>
  <circle cx="512" cy="740" r="15" fill="none" stroke="#000" stroke-width="2.5"/>
  <!-- Swirling bubbles left -->
  <circle cx="250" cy="350" r="14" fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="220" cy="400" r="9"  fill="none" stroke="#000" stroke-width="2"/>
  <circle cx="270" cy="430" r="11" fill="none" stroke="#000" stroke-width="2"/>
  <!-- Swirling bubbles right -->
  <circle cx="770" cy="360" r="12" fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="800" cy="410" r="16" fill="none" stroke="#000" stroke-width="2.5"/>
  <circle cx="758" cy="448" r="8"  fill="none" stroke="#000" stroke-width="2"/>
  <!-- Diagonal swirl lines (give depth) -->
  <path d="M 160,240 Q 300,220 390,280 Q 340,240 280,260"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>
  <path d="M 864,240 Q 724,220 634,280 Q 684,240 744,260"
        fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"/>""",

    "page-9-starfish": """\
  <!-- Scene: Starfish beach / ocean floor -->
  <!-- Large starfish (center-left) -->
  <path d="M 220,820 L 240,750 L 280,820 L 220,780 L 300,780 Z"
        fill="white" stroke="#000" stroke-width="3" stroke-linejoin="round"/>
  <!-- Starfish arm texture dots -->
  <circle cx="230" cy="795" r="4" fill="none" stroke="#000" stroke-width="1.5"/>
  <circle cx="260" cy="782" r="4" fill="none" stroke="#000" stroke-width="1.5"/>
  <circle cx="265" cy="808" r="4" fill="none" stroke="#000" stroke-width="1.5"/>
  <!-- Second starfish (right) -->
  <path d="M 720,860 L 748,792 L 776,860 L 716,818 L 790,818 Z"
        fill="white" stroke="#000" stroke-width="3" stroke-linejoin="round"/>
  <!-- Starfish 2 texture -->
  <circle cx="732" cy="835" r="4" fill="none" stroke="#000" stroke-width="1.5"/>
  <circle cx="753" cy="824" r="4" fill="none" stroke="#000" stroke-width="1.5"/>
  <!-- Sand dollar 1 -->
  <circle cx="380" cy="920" r="38" fill="white" stroke="#000" stroke-width="3"/>
  <circle cx="380" cy="920" r="24" fill="none" stroke="#000" stroke-width="2"/>
  <path d="M 380,896 L 380,944 M 356,920 L 404,920 M 363,903 L 397,937 M 363,937 L 397,903"
        fill="none" stroke="#000" stroke-width="1.8"/>
  <!-- Sand dollar 2 (smaller) -->
  <circle cx="660" cy="935" r="28" fill="white" stroke="#000" stroke-width="3"/>
  <circle cx="660" cy="935" r="17" fill="none" stroke="#000" stroke-width="2"/>
  <path d="M 660,917 L 660,953 M 642,935 L 678,935"
        fill="none" stroke="#000" stroke-width="1.8"/>
  <!-- Seashell -->
  <path d="M 500,950 Q 480,930 490,910 Q 510,900 530,910 Q 540,930 520,950 Z"
        fill="white" stroke="#000" stroke-width="2.5"/>
  <path d="M 490,930 Q 510,922 530,930" fill="none" stroke="#000" stroke-width="1.8"/>
  <path d="M 492,942 Q 510,936 528,942" fill="none" stroke="#000" stroke-width="1.8"/>
  <!-- Sandy ocean floor -->
  <path d="M 0,975 Q 256,960 512,968 Q 768,976 1024,960 L 1024,1024 L 0,1024 Z"
        fill="white" stroke="#000" stroke-width="3"/>
  <!-- Sand ripple texture -->
  <path d="M 100,985 Q 200,980 300,986" fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M 600,990 Q 720,984 840,991" fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>""",
}

# Map scene key -> output filename
_PAGES = {
    "page-5-forest":   "page-5-forest.svg",
    "page-6-treasure": "page-6-treasure.svg",
    "page-7-jellyfish":"page-7-jellyfish.svg",
    "page-8-whirlpool":"page-8-whirlpool.svg",
    "page-9-starfish": "page-9-starfish.svg",
}


def _build_svg(scene_key: str) -> str:
    """Return a complete 1024x1024 B&W placeholder SVG for the given scene."""
    scene_elements = _SCENE_ELEMENTS[scene_key]
    return textwrap.dedent(f"""\
        <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
             width="1024" height="1024" viewBox="0 0 1024 1024">
          <!-- B&W outline placeholder for coloring: {scene_key} -->
          <!-- Generated by scripts/generate_coloring_placeholders.py -->
          <rect width="1024" height="1024" fill="white"/>

        {_MERMAID_BODY}

        {scene_elements}
        </svg>
    """)


def generate(output_dir: Path, force: bool = False) -> list[Path]:
    """Write placeholder SVGs to output_dir. Returns list of written paths.

    Args:
        output_dir: Directory to write SVGs into (must already exist).
        force: If True, overwrite existing files. Default False.

    Raises:
        OSError: if a file cannot be written. The error is printed to stderr
                 and the function re-raises so callers can detect failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []

    for scene_key, filename in _PAGES.items():
        out = output_dir / filename
        if out.exists() and not force:
            # Check if it's a stub (< 500 bytes) — always replace stubs
            if out.stat().st_size >= 500:
                print(f"  Skip (exists, {out.stat().st_size:,}B): {filename}")
                results.append(out)
                continue

        svg_content = _build_svg(scene_key)
        try:
            out.write_text(svg_content, encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: failed to write {out}: {exc}", file=sys.stderr)
            raise

        path_count = svg_content.count("<path")
        size = out.stat().st_size
        status = "✓ replaced stub" if size < 1000 else "✓ created"
        print(f"  {status}: {filename}  ({size:,}B, {path_count} paths)")
        results.append(out)

    return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate scene-themed B&W coloring SVGs for pages 5-9."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files (even non-stubs).",
    )
    args = parser.parse_args()

    print(f"Output directory: {OUTPUT_DIR}")
    print("Generating placeholder coloring SVGs...")

    try:
        results = generate(OUTPUT_DIR, force=args.force)
    except OSError:
        sys.exit(1)

    print(f"\nDone: {len(results)} SVG(s) written/verified.")

    # Diagnostic: print path counts for all generated files
    print("\nContent summary:")
    for path in sorted(results):
        content = path.read_text(encoding="utf-8")
        path_count = content.count("<path")
        size = path.stat().st_size
        ok = "✅" if path_count >= 5 else "❌"
        print(f"  {ok} {path.name}: {size:,}B, {path_count} paths")


if __name__ == "__main__":
    main()
