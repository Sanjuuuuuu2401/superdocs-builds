# Miro Board to Structured Document

A SuperDocs extension that reads a Miro board through the Miro REST API and converts workshop content into a structured, traceable document.

## What it does

The extension:

1. Fetches items from a Miro board using the Miro REST API.
2. Supports processing the entire board or a selected frame.
3. Groups sticky notes by their parent Miro frame.
4. Detects semantic section names from the content.
5. Removes duplicate sticky notes.
6. Preserves the original Miro item IDs for traceability.
7. Generates a structured Markdown workshop summary.
8. Reuses unchanged sections between runs.
9. Regenerates only sections affected by board changes.
10. Can write a generated-document summary back onto the Miro board.

## Example

A Miro board containing:

* Customer Problems
* Ideas
* Questions

is converted into:

```text
# Miro Workshop Summary

## Customer Problems

- Checkout is extremely slow
  - Source: Miro sticky note `3458764681061461126`

- Payment sometimes fails
  - Source: Miro sticky note `3458764681061461276`

## Questions

- Why are payments failing?
  - Source: Miro sticky note `3458764681062252495`

## Ideas

- Add Apple Pay
  - Source: Miro sticky note `3458764681061823482`
```

## Architecture

```text
Miro Board
    |
    v
Miro REST API
    |
    v
miro_parser.py
    |
    v
Parsed Miro items
    |
    v
document_builder.py
    |
    v
Structured sections
    |
    +--------------------+
    |                    |
    v                    v
section_detector.py   Incremental cache
    |                    |
    +---------+----------+
              |
              v
    document_generator.py
              |
       +------+------+
       |             |
       v             v
   Markdown        HTML
       |
       v
output/
```

## Files

### `miro_parser.py`

Fetches Miro board items and converts the API response into a simplified internal representation.

It handles:

* Miro authentication
* pagination
* HTML cleanup
* item types
* source IDs
* parent frame IDs

### `document_builder.py`

Builds the structured document.

It:

* collects frames
* attaches sticky notes to their parent frames
* removes duplicates
* detects semantic section titles
* preserves source IDs

### `section_detector.py`

Determines a meaningful section name from the sticky-note content.

Examples:

* Customer Problems
* Questions
* Ideas

### `document_generator.py`

Controls the complete document-generation workflow.

It supports:

```text
python document_generator.py
```

to process the entire board.

A specific frame can also be selected:

```text
python document_generator.py FRAME_ID
```

The generator uses a section-level cache to avoid regenerating unchanged sections.

### `miro_writer.py`

Writes a generated-document summary back onto the Miro board.

### `group_items.py`

Provides grouping functionality for board items.

### `board_structure.py`

Provides board-structure inspection utilities.

### `models.py`

Contains simple internal data models.

### `test_miro.py`

Contains basic tests for the Miro extension.

## Incremental updates

The extension stores a cache at:

```text
output/.section_cache.json
```

Each section receives a SHA-256 fingerprint based on:

* Miro frame ID
* section title
* sticky-note source IDs
* sticky-note content

If a section has not changed, the previously generated Markdown is reused.

For example:

```text
First run:

Customer Problems → generated
Questions         → generated
Ideas             → generated


Second run:

Customer Problems → reused
Questions         → reused
Ideas             → reused


After changing one Customer Problems sticky:

Customer Problems → generated
Questions         → reused
Ideas             → reused
```

This allows large workshop boards to be updated without regenerating every section.

## Traceability

Every generated sticky note includes its original Miro item ID:

```text
- Checkout is extremely slow
  - Source: Miro sticky note `3458764681061461126`
```

This allows users to trace generated content back to its original board item.

## Configuration

Create a `.env` file in this extension directory:

```text
MIRO_ACCESS_TOKEN=your_miro_access_token
MIRO_BOARD_ID=your_miro_board_id
```

The `.env` file must never be committed to Git.

## Running locally

Create/activate the virtual environment and install dependencies.

Then run:

```text
python document_generator.py
```

For a selected frame:

```text
python document_generator.py FRAME_ID
```

To inspect the board structure:

```text
python miro_parser.py
```

## Output

Generated files are written to:

```text
output/
```

The primary generated document is:

```text
output/miro_document.md
```

## Miro API

The extension uses the Miro REST API to retrieve board items and create text items on the board.

Authentication is performed using a Miro access token stored in `.env`.

## Current limitations

### Voting

The current Miro `/items` response used by this extension does not expose generic board voting information as a normal item field.

The parser therefore preserves a `votes` value when available, but does not fabricate vote counts when the API does not provide them.

### Images

Image-item extraction and embedding can be added when image items are present on the configured Miro board.

The current demonstration board contains frames, sticky notes, shapes and text items but no image item.

## Security

Credentials are loaded from environment variables.

Never commit:

```text
.env
```

or any Miro access token.

The repository `.gitignore` excludes environment files and Python virtual-environment artifacts.
