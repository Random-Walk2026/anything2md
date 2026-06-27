from pathlib import Path

from anything2md.converter import ConvertOptions, convert
from anything2md.utils import check_pandoc

ROOT = Path(__file__).parent

check_pandoc()

convert(
    input_path=ROOT / "docx",
    opts=ConvertOptions(
        output_dir=ROOT / "markdown",
        recursive=True,
        overwrite=False,  # already converted files are skipped automatically
    ),
)
