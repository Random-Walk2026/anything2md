SUPPORTED_INPUT_FORMATS = {
    ".epub": "epub",
    ".docx": "docx",
    ".html": "html",
    ".htm":  "html",
    ".odt":  "odt",
    ".rtf":  "rtf",
    ".txt":  "markdown",
    ".md":   "markdown",
    # experimental — Pandoc PDF support is best-effort, no OCR
    ".pdf":  "pdf",
}

# Formats that benefit from --extract-media
MEDIA_EXTRACTABLE = {"epub", "docx", "html", "odt"}

# Formats marked as experimental; users will see a warning
EXPERIMENTAL_FORMATS = {"pdf"}
