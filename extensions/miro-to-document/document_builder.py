from miro_parser import get_board_items, parse_items
from section_detector import detect_section_title


def normalize_text(text):
    """
    Normalize text so we can compare similar sticky notes.
    """

    if not text:
        return ""

    text = text.lower().strip()

    # Remove accidental trailing characters
    text = text.rstrip("n").strip()

    # Normalize whitespace
    text = " ".join(text.split())

    return text


def deduplicate_items(items):
    """
    Remove duplicate sticky-note content.

    Duplicate detection is case-insensitive and
    whitespace-insensitive.
    """

    seen = set()
    unique_items = []

    for item in items:

        normalized = normalize_text(item["text"])

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_items.append(item)

    return unique_items


def build_document_structure(items):
    """
    Build a structured document from Miro frames
    and sticky notes.
    """

    # ---------------------------------------------------------
    # STEP 1: Collect frames
    # ---------------------------------------------------------

    frames = {}

    for item in items:

        if item["type"] == "frame":

            frames[item["id"]] = {
                "id": item["id"],
                "original_title": item["title"] or "Untitled Frame",
                "title": item["title"] or "Untitled Frame",
                "items": []
            }

    # ---------------------------------------------------------
    # STEP 2: Attach sticky notes to frames
    # ---------------------------------------------------------

    for item in items:

        if item["type"] != "sticky_note":
            continue

        parent_id = item["parent_id"]

        if parent_id not in frames:
            continue

        text = item["text"].strip()

        if not text:
            continue

        frames[parent_id]["items"].append({
            "source_id": item["id"],
            "text": text
        })

    # ---------------------------------------------------------
    # STEP 3: Remove duplicates INSIDE each frame
    # ---------------------------------------------------------

    for frame in frames.values():

        frame["items"] = deduplicate_items(
            frame["items"]
        )

    # ---------------------------------------------------------
    # STEP 4: Detect semantic section title
    # ---------------------------------------------------------

    document = []

    for frame in frames.values():

        if not frame["items"]:
            continue

        frame["title"] = detect_section_title(
            frame["items"]
        )

        document.append(frame)

    # ---------------------------------------------------------
    # STEP 5: Remove duplicate items across sections
    # ---------------------------------------------------------

    seen_content = set()

    cleaned_document = []

    for section in document:

        unique_items = []

        for item in section["items"]:

            normalized = normalize_text(
                item["text"]
            )

            if normalized in seen_content:
                continue

            seen_content.add(normalized)

            unique_items.append(item)

        if unique_items:

            section["items"] = unique_items

            cleaned_document.append(section)

    return cleaned_document


def print_document(document):

    print("\n========== DOCUMENT STRUCTURE ==========\n")

    for section in document:

        print(f"# {section['title']}")

        print(f"Frame ID: {section['id']}")

        print(
            f"Original Miro Title: "
            f"{section['original_title']}"
        )

        print()

        for item in section["items"]:

            print(f"- {item['text']}")

        print("\n" + "=" * 60)


if __name__ == "__main__":

    print("Fetching Miro board...")

    raw_items = get_board_items()

    items = parse_items(raw_items)

    document = build_document_structure(items)

    print_document(document)