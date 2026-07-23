from pathlib import Path

from .utils import log


def run_markitdown(
    input_path: Path,
    output_path: Path,
    verbose: bool,
) -> None:
    """Convert a file to Markdown with Microsoft MarkItDown.

    Used for PDF, which Pandoc cannot read directly, and for HTML where it
    strips presentational layout noise. MarkItDown does not OCR scanned or
    image-only PDFs (those come through nearly empty and need OCR first).
    """
    try:
        from markitdown import MarkItDown
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "markitdown is not installed. Install it with:\n"
            '  pip install "markitdown[pdf]"'
        ) from exc

    log(verbose, f"MarkItDown().convert({input_path!s}) -> {output_path!s}")

    result = MarkItDown().convert(str(input_path))
    output_path.write_text(result.text_content, encoding="utf-8")
