import argparse
from pathlib import Path

from .converter import ConvertOptions, convert
from .formats import SUPPORTED_INPUT_FORMATS
from .utils import check_pandoc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anything2md",
        description="Convert EPUB, DOCX, HTML and other documents to Markdown via Pandoc.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input file or directory",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        dest="output_dir",
        metavar="OUTPUT_DIR",
        help="Output directory for generated Markdown files",
    )
    parser.add_argument(
        "--to",
        default="gfm",
        metavar="FORMAT",
        help="Pandoc output format (default: gfm)",
    )
    parser.add_argument(
        "--from",
        default=None,
        dest="from_fmt",
        metavar="FORMAT",
        help="Force input format (auto-detected from extension by default)",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan subdirectories",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files",
    )
    parser.add_argument(
        "--extract-media",
        action="store_true",
        default=True,
        dest="extract_media",
        help="Extract embedded media (default: enabled)",
    )
    parser.add_argument(
        "--no-extract-media",
        action="store_false",
        dest="extract_media",
        help="Disable media extraction",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show pandoc commands and extra detail",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    check_pandoc()

    input_path: Path = args.input
    if not input_path.exists():
        parser.error(f"Input path does not exist: {input_path}")

    opts = ConvertOptions(
        output_dir=args.output_dir,
        to_fmt=args.to,
        from_fmt=args.from_fmt,
        recursive=args.recursive,
        overwrite=args.overwrite,
        extract_media=args.extract_media,
        verbose=args.verbose,
    )

    convert(input_path, opts)
