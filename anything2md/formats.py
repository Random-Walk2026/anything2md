SUPPORTED_INPUT_FORMATS = {
    ".epub": "epub",
    ".docx": "docx",
    ".html": "html",
    ".htm":  "html",
    ".odt":  "odt",
    ".rtf":  "rtf",
    ".txt":  "markdown",
    ".md":   "markdown",
    ".pdf":  "pdf",
}

# Formats routed through Microsoft MarkItDown instead of Pandoc. MarkItDown
# targets clean, LLM-friendly Markdown: Pandoc cannot read PDF at all, and on
# presentational HTML (CSS-heavy pages / slide decks) Pandoc passes raw <div>
# noise through, whereas MarkItDown strips it to plain text.
MARKITDOWN_FORMATS = {"pdf", "html"}

# Of the MarkItDown formats, only these can be scanned images and benefit from
# OCR (i.e. PDF). HTML is always text, so it never goes through OCR.
OCR_FORMATS = {"pdf"}

# Formats that benefit from Pandoc's --extract-media
MEDIA_EXTRACTABLE = {"epub", "docx", "odt"}
