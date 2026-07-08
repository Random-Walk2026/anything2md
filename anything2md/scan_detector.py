# Below this many non-whitespace characters, a PDF's MarkItDown output is
# treated as having no usable text layer — i.e. a scanned / image-only PDF
# that needs OCR before it can be converted to Markdown.
SCANNED_TEXT_THRESHOLD = 200


def looks_scanned(markdown_text: str, threshold: int = SCANNED_TEXT_THRESHOLD) -> bool:
    """Heuristic scan detector.

    A copyable-text PDF yields plenty of extractable text through MarkItDown;
    a scanned (image-only) PDF yields almost nothing. We count non-whitespace
    characters in the already-produced Markdown, so no extra dependency or
    second pass over the source is needed.
    """
    meaningful = sum(1 for ch in markdown_text if not ch.isspace())
    return meaningful < threshold
