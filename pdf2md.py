from pathlib import Path

from anything2md.converter import ConvertOptions, convert

ROOT = Path(__file__).parent

# PDFs are routed through MarkItDown (see anything2md/formats.py), so no pandoc
# check is needed here.
convert(
    input_path=ROOT / "pdfs",
    opts=ConvertOptions(
        output_dir=ROOT / "markdown",
        recursive=True,
        overwrite=False,  # already converted files are skipped automatically
    ),
)
