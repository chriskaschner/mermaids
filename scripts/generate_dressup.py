"""Generate 9 diverse kawaii mermaid character PNGs via gpt-image-1.

Thin CLI entry point that calls generate_dressup_characters() from the
pipeline module. Produces 9 standalone full-color character PNGs.
Re-running skips already-generated files.

Usage:
    uv run python scripts/generate_dressup.py
"""

from mermaids.pipeline.generate import generate_dressup_characters


def main():
    print("Generating 9 dress-up characters...")
    results = generate_dressup_characters()

    print(f"\nDone: {len(results)} character(s) processed.")
    for r in results:
        print(f"  {r.name}")


if __name__ == "__main__":
    main()
