from pathlib import Path

from document_builder import build_document_structure
from miro_parser import get_board_items, parse_items


def clean_text(text):
    """
    Clean formatting artifacts from Miro text.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove accidental trailing 'n'
    if text.endswith("n") and not text.endswith(" in"):
        text = text[:-1].rstrip()

    # Normalize whitespace
    text = " ".join(text.split())

    return text


def generate_markdown(document):
    """
    Convert the structured Miro document into Markdown.

    Each item includes its original Miro source ID
    so the generated document remains traceable.
    """

    lines = []

    lines.append("# Miro Workshop Summary")
    lines.append("")

    lines.append(
        "> Automatically generated from the Miro board."
    )

    lines.append(
        "> Each item includes its original Miro source ID."
    )

    lines.append("")

    for section in document:

        lines.append(
            f"## {section['title']}"
        )

        lines.append("")

        for item in section["items"]:

            text = clean_text(
                item["text"]
            )

            source_id = item["source_id"]

            lines.append(
                f"- {text}"
            )

            lines.append(
                f"  - Source: Miro sticky note `{source_id}`"
            )

        lines.append("")

    return "\n".join(lines)


def save_document(content):
    """
    Save the generated Markdown document.
    """

    output_dir = Path("output")

    output_dir.mkdir(
        exist_ok=True
    )

    output_file = (
        output_dir /
        "miro_document.md"
    )

    output_file.write_text(
        content,
        encoding="utf-8"
    )

    return output_file


if __name__ == "__main__":

    print("Fetching Miro board...")

    raw_items = get_board_items()

    items = parse_items(
        raw_items
    )

    document = build_document_structure(
        items
    )

    markdown = generate_markdown(
        document
    )

    output_file = save_document(
        markdown
    )

    print()
    print(
        "Document generated successfully!"
    )

    print(
        f"Output: {output_file}"
    )

    print()
    print(
        "========== GENERATED DOCUMENT =========="
    )

    print()

    print(markdown)