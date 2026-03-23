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
    {
        "id": "page-5-forest",
        "prompt_detail": (
            "A chibi kawaii mermaid with curly afro puffs hair and sparkle eyes "
            "swimming through a tall kelp forest, with a star-shaped tail fin. "
            "The mermaid's hair is a single enclosed shape with a clear black outline. "
            "The mermaid's tail is a single enclosed shape with a clear black outline."
        ),
    },
    {
        "id": "page-6-treasure",
        "prompt_detail": (
            "A chibi kawaii mermaid with long braids adorned with beads and wide eyes "
            "discovering a treasure chest on the ocean floor, with a rounded fin tail. "
            "The mermaid's hair is a single enclosed shape with a clear black outline. "
            "The mermaid's tail is a single enclosed shape with a clear black outline."
        ),
    },
    {
        "id": "page-7-jellyfish",
        "prompt_detail": (
            "A chibi kawaii mermaid with coily hair and a flower tucked in and bright eyes "
            "floating among glowing jellyfish in a meadow, with a flowing tail. "
            "The mermaid's hair is a single enclosed shape with a clear black outline. "
            "The mermaid's tail is a single enclosed shape with a clear black outline."
        ),
    },
    {
        "id": "page-8-whirlpool",
        "prompt_detail": (
            "A chibi kawaii mermaid with silver locs with ocean-blue tips and big bright eyes "
            "riding a whirlpool vortex surrounded by swirling bubbles, with a deep fin tail. "
            "The mermaid's hair is a single enclosed shape with a clear black outline. "
            "The mermaid's tail is a single enclosed shape with a clear black outline."
        ),
    },
    {
        "id": "page-9-starfish",
        "prompt_detail": (
            "A chibi kawaii mermaid with a short bob with bangs and starry eyes "
            "resting on a starfish beach with sand dollars all around, with an iridescent tail. "
            "The mermaid's hair is a single enclosed shape with a clear black outline. "
            "The mermaid's tail is a single enclosed shape with a clear black outline."
        ),
    },
]

# ---------------------------------------------------------------------------
# Dress-up: 9 diverse full-color chibi kawaii mermaid characters
# ---------------------------------------------------------------------------

DRESSUP_BASE_PROMPT: str = (
    "Full color chibi kawaii mermaid character, flat cell-shaded style with "
    "solid color fills. Big head, small body, Sanrio-like cute proportions. "
    "Neutral front-facing pose, centered, white background. Clean edges between "
    "color regions suitable for SVG tracing. "
)

DRESSUP_CHARACTERS: list[dict[str, str]] = [
    {
        "id": "mermaid-1",
        "prompt_detail": (
            "Light fair skin, long flowing wavy golden blonde hair, big round "
            "blue eyes, pastel pink fish tail with rounded fins, pearl necklace"
        ),
    },
    {
        "id": "mermaid-2",
        "prompt_detail": (
            "Light fair skin with freckles, twin red pigtails with bows, big "
            "green eyes, lavender purple ribbon-like tail, starfish hairpin"
        ),
    },
    {
        "id": "mermaid-3",
        "prompt_detail": (
            "Medium olive skin, long dark brown curly hair, big warm brown eyes, "
            "teal green tail with scalloped edges, flower garland around shoulders"
        ),
    },
    {
        "id": "mermaid-4",
        "prompt_detail": (
            "Medium tan skin, straight black hair in a long braid, big dark "
            "brown eyes, coral orange tail with fan-shaped fin, seashell crown"
        ),
    },
    {
        "id": "mermaid-5",
        "prompt_detail": (
            "Medium brown skin, dark curly afro puffs tied with ribbons, big "
            "sparkle brown eyes, aqua blue star-shaped tail, bubble wand in hand"
        ),
    },
    {
        "id": "mermaid-6",
        "prompt_detail": (
            "Brown skin, black hair in long braids with gold beads, big warm "
            "dark eyes, golden yellow tail with rounded fins, shell earrings"
        ),
    },
    {
        "id": "mermaid-7",
        "prompt_detail": (
            "Deep brown skin, dark coily hair with a flower tucked in, big "
            "bright brown eyes, magenta pink tail with flowing fins, pearl tiara"
        ),
    },
    {
        "id": "mermaid-8",
        "prompt_detail": (
            "Dark rich skin, silver-white locs with ocean-blue tips, big bright "
            "eyes, deep purple tail with sparkle accents, tiny seahorse companion "
            "on shoulder"
        ),
    },
    {
        "id": "mermaid-9",
        "prompt_detail": (
            "Light warm skin, short mint green bob with bangs and a seashell "
            "clip, big starry eyes, rainbow iridescent tail, holding a small "
            "jellyfish friend"
        ),
    },
]
