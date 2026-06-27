import glob
from pathlib import Path

import pypandoc

from .utils import log


def run_pandoc(
    input_path: Path,
    output_path: Path,
    from_fmt: str,
    to_fmt: str,
    extract_media: bool,
    media_dir: Path | None,
    verbose: bool,
) -> None:
    extra_args: list[str] = []
    escaped_input = glob.escape(str(input_path))

    if extract_media and media_dir is not None:
        extra_args += [f"--extract-media={media_dir}"]

    log(verbose, f"pypandoc.convert_file({escaped_input!s}, to={to_fmt!r}, format={from_fmt!r}, outputfile={output_path!s}, extra_args={extra_args})")

    pypandoc.convert_file(
        escaped_input,
        to=to_fmt,
        format=from_fmt,
        outputfile=str(output_path),
        extra_args=extra_args,
    )
