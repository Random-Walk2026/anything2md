#!/usr/bin/env python3
"""anything2md book pipeline.

Steps:
  convert    epubs/<Folder>/ -> markdown/<Folder>/  (Markdown via pandoc, mirrors folders)
             pdfs/<Folder>/  -> markdown/<Folder>/  (Markdown via MarkItDown)
  organize   re-file existing markdown/ to mirror epubs/ folders
  intros     markdown/ -> intros/<Folder>/<book>/website.md + generic.md
                                            (Gemini reads each book and writes
                                             a 1000-word intro, fully automatic)
  all        convert + organize + intros

Typical run:
  python pipeline.py all                   # everything
  python pipeline.py intros --only KEYWORD # (re)generate one matching book
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).parent
EPUBS = ROOT / "epubs"
PDFS = ROOT / "pdfs"
MARKDOWN = ROOT / "markdown"
INTROS = ROOT / "intros"


def cmd_convert(ocr: bool = False) -> None:
    from anything2md.converter import ConvertOptions, convert
    from anything2md.utils import check_pandoc

    check_pandoc()
    opts = ConvertOptions(output_dir=MARKDOWN, recursive=True, overwrite=False, ocr=ocr)
    # EPUB/DOCX/… go through pandoc; PDFs are routed to MarkItDown internally,
    # with scanned PDFs sent through OCRmyPDF first when --ocr is set.
    convert(input_path=EPUBS, opts=opts)
    if PDFS.exists():
        convert(input_path=PDFS, opts=opts)


def cmd_organize(dry_run: bool) -> None:
    from anything2md.organize import organize

    organize(MARKDOWN, EPUBS, dry_run=dry_run)


def cmd_intros(overwrite: bool, only: str | None) -> None:
    from md2intro.runner import generate_intros

    generate_intros(MARKDOWN, INTROS, overwrite=overwrite, only=only)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="EPUB -> Markdown -> topic folders -> Gemini intros.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="Convert epubs/ and pdfs/ into markdown/")
    p_conv.add_argument("--ocr", action="store_true",
                        help="OCR scanned PDFs first (requires ocrmypdf + Tesseract)")

    p_org = sub.add_parser("organize", help="Sort markdown/ into topic folders")
    p_org.add_argument("--dry-run", action="store_true", help="Preview moves only")

    p_int = sub.add_parser("intros", help="Generate book intros with Gemini")
    p_int.add_argument("--overwrite", action="store_true",
                       help="Regenerate even if website.md already exists")
    p_int.add_argument("--only", metavar="SUBSTR",
                       help="Only books whose filename contains SUBSTR")

    p_all = sub.add_parser("all", help="convert + organize + intros")
    p_all.add_argument("--ocr", action="store_true",
                       help="OCR scanned PDFs first (requires ocrmypdf + Tesseract)")

    args = parser.parse_args()

    if args.command == "convert":
        cmd_convert(args.ocr)
    elif args.command == "organize":
        cmd_organize(args.dry_run)
    elif args.command == "intros":
        cmd_intros(args.overwrite, args.only)
    elif args.command == "all":
        cmd_convert(args.ocr)
        print("\n" + "=" * 50 + "\n")
        cmd_organize(dry_run=False)
        print("\n" + "=" * 50 + "\n")
        cmd_intros(overwrite=False, only=None)


if __name__ == "__main__":
    main()
