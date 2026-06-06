from dataclasses import dataclass, field
from pathlib import Path

from .formats import EXPERIMENTAL_FORMATS, MEDIA_EXTRACTABLE, SUPPORTED_INPUT_FORMATS
from .pandoc_runner import run_pandoc
from .utils import ensure_dir, log, slugify


@dataclass
class ConvertOptions:
    output_dir: Path
    to_fmt: str = "gfm"
    from_fmt: str | None = None
    recursive: bool = False
    overwrite: bool = False
    extract_media: bool = True
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

    for src in files:
        _convert_file(src, opts, summary)

    summary.print()
    return summary


def _convert_file(src: Path, opts: ConvertOptions, summary: Summary) -> None:
    suffix = src.suffix.lower()
    from_fmt = opts.from_fmt or SUPPORTED_INPUT_FORMATS.get(suffix)

    if from_fmt is None:
        msg = f"unsupported format: {suffix}"
        print(f"Skipped: {src} — {msg}")
        summary.skipped += 1
        return

    slug = slugify(src.stem)
    out_file = opts.output_dir / f"{slug}.md"
    media_dir = opts.output_dir / f"{slug}_media" if opts.extract_media else None

    if out_file.exists() and not opts.overwrite:
        print(f"Skipped: {out_file} already exists (use --overwrite to replace)")
        summary.skipped += 1
        return

    if from_fmt in EXPERIMENTAL_FORMATS:
        print(f"Warning: PDF conversion is experimental and may produce poor Markdown structure. ({src})")

    do_extract = opts.extract_media and from_fmt in MEDIA_EXTRACTABLE

    try:
        log(opts.verbose, f"Converting: {src} -> {out_file}")
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
