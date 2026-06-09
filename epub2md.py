from pathlib import Path

from doc2md.converter import ConvertOptions, convert
from doc2md.utils import check_pandoc

ROOT = Path(__file__).parent

check_pandoc()

convert(
    input_path=ROOT / "epubs",
    opts=ConvertOptions(
        output_dir=ROOT / "markdown",
        recursive=True,
        overwrite=False,   # already converted files are skipped automatically
    ),
)
