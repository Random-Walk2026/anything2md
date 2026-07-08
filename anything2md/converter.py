from dataclasses import dataclass, field
from pathlib import Path

from .formats import (
    MARKITDOWN_FORMATS,
    MEDIA_EXTRACTABLE,
    OCR_FORMATS,
    SUPPORTED_INPUT_FORMATS,
)
from .markitdown_runner import run_markitdown
from .ocr_runner import OCR_LANGUAGES, run_ocrmypdf
from .pandoc_runner import run_pandoc
from .scan_detector import looks_scanned
from .utils import ensure_dir, log, slugify


@dataclass
class ConvertOptions:
    output_dir: Path
    to_fmt: str = "gfm"
    from_fmt: str | None = None
    recursive: bool = False
    overwrite: bool = False
    extract_media: bool = True
    ocr: bool = False                       # OCR scanned PDFs (needs ocrmypdf)
    ocr_languages: str = OCR_LANGUAGES
    verbose: bool = False


@dataclass
class Summary:
    total: int = 0
    success: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[tuple[Path, str]] = field(default_factory=list)

    def print(self) -> None:
        print(f"\nTotal:   {self.total}")
        print(f"Success: {self.success}")
        print(f"Skipped: {self.skipped}")
        print(f"Failed:  {self.failed}")
        if self.errors:
            print("\nFailed files:")
            for path, msg in self.errors:
                print(f"  {path}: {msg}")


def _existing_output(output_dir: Path, slug: str) -> Path | None:
    """Return an existing ``<slug>.md`` anywhere under output_dir (incl. topic
    subfolders), so re-running convert skips books already filed by organize."""
    name = f"{slug}.md"
    direct = output_dir / name
    if direct.exists():
        return direct
    return next((p for p in output_dir.glob(f"**/{name}") if p.is_file()), None)


def _collect_files(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]

    pattern = "**/*" if recursive else "*"
    return [
        f
        for f in input_path.glob(pattern)
        if f.is_file() and f.suffix.lower() in SUPPORTED_INPUT_FORMATS
    ]


def convert(input_path: Path, opts: ConvertOptions) -> Summary:
    files = _collect_files(input_path, opts.recursive)
    summary = Summary(total=len(files))
    ensure_dir(opts.output_dir)

    # Mirror the source folder layout: epubs/<Folder>/x.epub -> markdown/<Folder>/x.md
    input_root = input_path if input_path.is_dir() else input_path.parent

    for src in files:
        _convert_file(src, input_root, opts, summary)

    summary.print()
    return summary


def _convert_file(
    src: Path, input_root: Path, opts: ConvertOptions, summary: Summary
) -> None:
    suffix = src.suffix.lower()
    from_fmt = opts.from_fmt or SUPPORTED_INPUT_FORMATS.get(suffix)

    if from_fmt is None:
        msg = f"unsupported format: {suffix}"
        print(f"Skipped: {src} — {msg}")
        summary.skipped += 1
        return

    slug = slugify(src.stem)
    rel_parent = src.parent.relative_to(input_root)
    out_dir = opts.output_dir / rel_parent
    out_file = out_dir / f"{slug}.md"
    media_dir = out_dir / f"{slug}_media" if opts.extract_media else None

    if not opts.overwrite:
        existing = _existing_output(opts.output_dir, slug)
        if existing is not None:
            print(f"Skipped: {existing} already exists (use --overwrite to replace)")
            summary.skipped += 1
            return

    use_markitdown = from_fmt in MARKITDOWN_FORMATS
    do_extract = opts.extract_media and from_fmt in MEDIA_EXTRACTABLE

    ensure_dir(out_dir)
    try:
        log(opts.verbose, f"Converting: {src} -> {out_file}")
        if use_markitdown:
            if not _convert_markitdown(
                src, out_file, out_dir, slug, from_fmt, opts, summary
            ):
                return
        else:
            run_pandoc(
                input_path=src,
                output_path=out_file,
                from_fmt=from_fmt,
                to_fmt=opts.to_fmt,
                extract_media=do_extract,
                media_dir=media_dir,
                verbose=opts.verbose,
            )
        print(f"OK: {src} -> {out_file}")
        summary.success += 1
    except Exception as exc:
        msg = str(exc)
        print(f"Failed: {src} — {msg}")
        summary.errors.append((src, msg))
        summary.failed += 1


def _convert_markitdown(
    src: Path, out_file: Path, out_dir: Path, slug: str, from_fmt: str,
    opts: ConvertOptions, summary: Summary,
) -> bool:
    """Convert via MarkItDown, OCR-ing first if a PDF looks scanned.

    Returns True if ``out_file`` now holds real Markdown, or False if the file
    was skipped (a scanned PDF with OCR not enabled) — in which case no empty
    ``.md`` is left behind, so a later ``--ocr`` run re-processes it. Non-PDF
    inputs (e.g. HTML) are always text and skip scan detection entirely.
    """
    run_markitdown(input_path=src, output_path=out_file, verbose=opts.verbose)

    if from_fmt not in OCR_FORMATS:
        return True

    if not looks_scanned(out_file.read_text(encoding="utf-8")):
        return True

    if not opts.ocr:
        out_file.unlink(missing_ok=True)
        print(f"Skipped: {src} looks scanned (no text layer) — "
              f"re-run with --ocr to OCR it first.")
        summary.skipped += 1
        return False

    # Scanned PDF: OCR into a cached searchable PDF, then re-extract.
    ocr_pdf = out_dir / f"{slug}.ocr.pdf"
    if opts.overwrite or not ocr_pdf.exists():
        run_ocrmypdf(src, ocr_pdf, languages=opts.ocr_languages, verbose=opts.verbose)
    run_markitdown(input_path=ocr_pdf, output_path=out_file, verbose=opts.verbose)
    return True
