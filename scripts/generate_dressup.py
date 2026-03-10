"""Generate kawaii mermaid dress-up variant PNGs via gpt-image-1 edit API.

Thin CLI entry point that calls generate_dressup_variants() from the
pipeline module. Produces a base mermaid + 9 variant PNGs (3 tails,
3 hair, 3 accessories). Re-running skips already-generated files.

Usage:
    uv run python scripts/generate_dressup.py
"""

from mermaids.pipeline.edit import generate_dressup_variants


def main():
    print("Generating dress-up base + variants...")
    results = generate_dressup_variants()

    print(f"\nDone: {len(results)} dress-up variant(s) processed.")
    for r in results:
        print(f"  {r.name}")


if __name__ == "__main__":
    main()
