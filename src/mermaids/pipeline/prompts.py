"""Prompt templates for kawaii mermaid art generation.

Contains base prompts and page/variant definitions for both coloring
page and dress-up asset generation via gpt-image-1.
"""

# ---------------------------------------------------------------------------
# Coloring pages: black-and-white outline art for children to color in
# ---------------------------------------------------------------------------

COLORING_BASE_PROMPT: str = (
    "Black and white coloring page outline art. Clean simple lines on white "
    "background. Chibi kawaii mermaid character with big head, small body, "
    "oversized round eyes, minimal detail, Sanrio-like cute style. No shading, "
    "no gradients, no fills -- only clean black outlines suitable for a child "
    "to color in. "
)

COLORING_PAGES: list[dict[str, str]] = [
    {
        "id": "page-1-ocean",
        "prompt_detail": "swimming in the ocean with small fish and bubbles around her",
    },
    {
        "id": "page-2-castle",
        "prompt_detail": "sitting on a rock near an underwater castle with towers and arches",
    },
    {
        "id": "page-3-seahorse",
        "prompt_detail": "riding a cute seahorse friend with seaweed in the background",
    },
    {
        "id": "page-4-coral",
        "prompt_detail": "playing among coral reef formations with starfish on the ground",
    },
]

# ---------------------------------------------------------------------------
# Dress-up: full-color chibi kawaii mermaid with flat fills for recoloring
# ---------------------------------------------------------------------------

DRESSUP_BASE_PROMPT: str = (
    "Full color chibi kawaii mermaid character, flat cell-shaded style with "
    "solid color fills. Big head, small body, oversized round eyes, Sanrio-like "
    "cute proportions. Clean edges between color regions suitable for SVG "
    "tracing. White background, centered, front-facing pose. "
)

DRESSUP_VARIANTS: dict[str, list[dict[str, str]]] = {
    "tails": [
        {"id": "tail-1", "prompt_detail": "classic fish tail with rounded fins, pastel pink"},
        {"id": "tail-2", "prompt_detail": "flowing ribbon-like tail with scalloped edges, lavender purple"},
        {"id": "tail-3", "prompt_detail": "star-shaped tail fin with sparkle accents, aqua blue"},
    ],
    "hair": [
        {"id": "hair-1", "prompt_detail": "long flowing wavy hair, golden blonde"},
        {"id": "hair-2", "prompt_detail": "twin pigtails with bows, coral pink"},
        {"id": "hair-3", "prompt_detail": "short bob with bangs and a seashell clip, mint green"},
    ],
    "accessories": [
        {"id": "acc-1", "prompt_detail": "pearl necklace and small tiara crown"},
        {"id": "acc-2", "prompt_detail": "flower garland around shoulders and a starfish hairpin"},
        {"id": "acc-3", "prompt_detail": "bubble wand in hand and tiny seahorse companion on shoulder"},
    ],
}
