#!/usr/bin/env python3
"""anything2md batch conversion pipeline.

Steps:
  convert    epubs/<Folder>/ -> markdown/<Folder>/  (Markdown via pandoc, mirrors folders)
             pdfs/<Folder>/  -> markdown/<Folder>/  (Markdown via MarkItDown)
  organize   re-file existing markdown/ to mirror source folders
  all        convert + organize

Typical run:
  python pipeline.py all
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).parent
EPUBS = ROOT / "epubs"
PDFS = ROOT / "pdfs"
MARKDOWN = ROOT / "markdown"
SOURCE_DIRS = (EPUBS, PDFS)


def cmd_convert(ocr: bool = False) -> None:
    from anything2md.converter import ConvertOptions, convert, requires_pandoc
    from anything2md.utils import check_pandoc

    if any(requires_pandoc(path, recursive=True) for path in SOURCE_DIRS):
        check_pandoc()
    opts = ConvertOptions(output_dir=MARKDOWN, recursive=True, overwrite=False, ocr=ocr)
    # EPUB/DOCX/… go through pandoc; PDFs are routed to MarkItDown internally,
    # with scanned PDFs sent through OCRmyPDF first when --ocr is set.
    convert(input_path=EPUBS, opts=opts)
    if PDFS.exists():
        convert(input_path=PDFS, opts=opts)


def cmd_organize(dry_run: bool) -> None:
    from anything2md.organize import organize

    organize(MARKDOWN, SOURCE_DIRS, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Batch-convert source folders and organize their Markdown output.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="Convert epubs/ and pdfs/ into markdown/")
    p_conv.add_argument("--ocr", action="store_true",
                        help="OCR scanned PDFs first (requires ocrmypdf + Tesseract)")

    p_org = sub.add_parser("organize", help="Sort markdown/ into source folders")
    p_org.add_argument("--dry-run", action="store_true", help="Preview moves only")

    p_all = sub.add_parser("all", help="convert + organize")
    p_all.add_argument("--ocr", action="store_true",
                       help="OCR scanned PDFs first (requires ocrmypdf + Tesseract)")

    args = parser.parse_args()

    if args.command == "convert":
        cmd_convert(args.ocr)
    elif args.command == "organize":
        cmd_organize(args.dry_run)
    elif args.command == "all":
        cmd_convert(args.ocr)
        print("\n" + "=" * 50 + "\n")
        cmd_organize(dry_run=False)


if __name__ == "__main__":
    main()
