import shutil
import subprocess
from pathlib import Path

from .utils import log

# Default OCR languages: simplified + traditional Chinese + English. Requires
# the matching Tesseract language packs (chi_sim / chi_tra / eng).
OCR_LANGUAGES = "chi_sim+chi_tra+eng"

_INSTALL_HINT = (
    "ocrmypdf is not installed (or not in PATH). Install it with:\n"
    "  macOS:  brew install ocrmypdf tesseract tesseract-lang\n"
    "  Ubuntu: sudo apt install ocrmypdf tesseract-ocr "
    "tesseract-ocr-chi-sim tesseract-ocr-chi-tra\n"
    "and make sure the Tesseract language packs are present."
)


def ocr_available() -> bool:
    """True if the ocrmypdf binary is on PATH."""
    return shutil.which("ocrmypdf") is not None


def run_ocrmypdf(
    input_path: Path,
    output_path: Path,
    languages: str = OCR_LANGUAGES,
    verbose: bool = False,
) -> None:
    """Add a searchable text layer to a scanned PDF with OCRmyPDF.

    Produces a new PDF at ``output_path`` (used as a cache) that MarkItDown can
    then read as ordinary text. ``--skip-text`` leaves pages that already carry
    a text layer untouched, so mixed PDFs are handled gracefully.
    """
    if not ocr_available():
        raise RuntimeError(_INSTALL_HINT)

    cmd = [
        "ocrmypdf",
        "-l", languages,
        "--deskew",
        "--rotate-pages",
        "--skip-text",
        str(input_path),
        str(output_path),
    ]
    log(verbose, f"run: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
