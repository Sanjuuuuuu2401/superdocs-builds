import os
import re
import requests
from dotenv import load_dotenv


load_dotenv()


def clean_html(html: str) -> str:
    """Convert Miro's HTML content into readable plain text."""

    if not html:
        return ""

    # Convert common HTML line breaks into spaces
    html = html.replace("<br />", " ")
    html = html.replace("<br>", " ")
    html = html.replace("</p>", " ")
    html = html.replace("</li>", " ")

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", html)

    # Decode common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#x1f7e6;", "🟦")
    text = text.replace("&#x1f7e9;", "🟩")
    text = text.replace("&#x1f7e8;", "🟨")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_board_items():
    """Fetch all items from the configured Miro board, handling pagination."""

    token = os.getenv("MIRO_ACCESS_TOKEN")
    board_id = os.getenv("MIRO_BOARD_ID")

    if not token:
        raise RuntimeError("MIRO_ACCESS_TOKEN is missing")

    if not board_id:
        raise RuntimeError("MIRO_BOARD_ID is missing")

    url = f"https://api.miro.com/v2/boards/{board_id}/items"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    all_items = []
    params = {
        "limit": 50
    }

    while True:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        if not response.ok:
            raise RuntimeError(
                f"Miro API request failed: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()

        items = data.get("data", [])

        all_items.extend(items)

        next_cursor = data.get("cursor")

        if not next_cursor:
            break

        params["cursor"] = next_cursor

    print(f"DEBUG: fetched {len(all_items)} items from Miro")

    return all_items

def parse_items(items):
    """Convert raw Miro items into a simple structured representation."""

    parsed = []

    for item in items:

        item_type = item.get("type")
        item_id = item.get("id")

        item_data = item.get("data", {})

        content = clean_html(
            item_data.get("content", "")
        )

        title = item_data.get("title")

        parent = item.get("parent")

        parent_id = None

        if parent:
            parent_id = parent.get("id")

        parsed.append({
            "id": item_id,
            "type": item_type,
            "text": content,
            "title": title,
            "parent_id": parent_id,
        })

    return parsed


def print_structure(items):
    """Display the board structure in a human-readable format."""

    print("\n========== MIRO BOARD STRUCTURE ==========\n")

    for item in items:

        print(f"TYPE: {item['type']}")
        print(f"ID: {item['id']}")

        if item["title"]:
            print(f"TITLE: {item['title']}")

        if item["text"]:
            print(f"TEXT: {item['text']}")

        if item["parent_id"]:
            print(f"PARENT: {item['parent_id']}")

        print("-" * 50)


if __name__ == "__main__":

    items = get_board_items()

    parsed = parse_items(items)

    print(f"Fetched {len(parsed)} Miro items.")

    print_structure(parsed)