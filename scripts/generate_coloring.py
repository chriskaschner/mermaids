"""Generate kawaii mermaid coloring page PNGs via gpt-image-1.

Thin CLI entry point that calls generate_coloring_pages() from the
pipeline module. Re-running skips already-generated files.

Usage:
    uv run python scripts/generate_coloring.py
"""

from mermaids.pipeline.generate import generate_coloring_pages


def main():
    print("Generating coloring pages...")
    results = generate_coloring_pages()

    generated = sum(1 for _ in results)
    print(f"\nDone: {generated} coloring page(s) processed.")


if __name__ == "__main__":
    main()
