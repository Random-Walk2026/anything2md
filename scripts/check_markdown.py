#!/usr/bin/env python3
"""Run lightweight, format-neutral checks on generated Markdown files.

The script intentionally has no project or AI dependencies. It reports empty
outputs, broken local image references, inconsistent GFM table widths, and
likely presentational HTML noise. Errors return exit code 1; warnings only
become failures when ``--strict`` is used.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\((?P<target><[^>]+>|[^\s)]+)(?:\s+['\"][^'\"]*['\"])?\)"
)
HTML_NOISE_RE = re.compile(
    r"<(?:div|span|section|article)\b[^>]*(?:style|class)\s*=",
    flags=re.IGNORECASE,
)
SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Markdown files to check")
    parser.add_argument(
        "--short-threshold",
        type=int,
        default=200,
        metavar="CHARS",
        help="warn below this many non-whitespace characters (default: 200)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as errors",
    )
    return parser.parse_args()


def local_image_path(markdown: Path, target: str) -> Path | None:
    target = target.strip("<>")
    if re.match(r"^[A-Za-z]:[\\/]", target):
        return Path(target)
    parsed = urlsplit(target)
    if parsed.scheme or target.startswith(("#", "//")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else markdown.parent / path


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    body = stripped[1:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def table_errors(lines: list[str]) -> list[str]:
    failures: list[str] = []
    index = 0
    while index + 1 < len(lines):
        header = table_cells(lines[index])
        separator = table_cells(lines[index + 1])
        if not header or not separator or not all(
            SEPARATOR_CELL_RE.fullmatch(cell) for cell in separator
        ):
            index += 1
            continue

        expected = len(header)
        row = index
        while row < len(lines):
            cells = table_cells(lines[row])
            if cells is None:
                break
            if len(cells) != expected:
                failures.append(
                    f"line {row + 1}: table has {len(cells)} columns; expected {expected}"
                )
            row += 1
        index = row
    return failures


def check_file(path: Path, short_threshold: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read file: {exc}"], warnings

    meaningful = sum(not char.isspace() for char in text)
    if meaningful == 0:
        errors.append("output is empty")
        return errors, warnings
    if meaningful < short_threshold:
        warnings.append(
            f"output is unusually short ({meaningful} non-whitespace characters)"
        )

    missing_images: set[str] = set()
    for match in IMAGE_RE.finditer(text):
        target = match.group("target")
        local = local_image_path(path, target)
        if local is not None and not local.exists():
            missing_images.add(target.strip("<>"))
    for target in sorted(missing_images):
        errors.append(f"missing local image: {target}")

    errors.extend(table_errors(text.splitlines()))

    html_noise = len(HTML_NOISE_RE.findall(text))
    if html_noise >= 3:
        warnings.append(
            f"found {html_noise} presentational HTML elements with class/style attributes"
        )

    return errors, warnings


def main() -> None:
    args = parse_args()
    failed = False

    for path in args.files:
        errors, warnings = check_file(path, max(0, args.short_threshold))
        print(f"{path}:")
        for message in errors:
            print(f"  ERROR: {message}")
        for message in warnings:
            print(f"  WARNING: {message}")
        if not errors and not warnings:
            print("  OK")
        failed = failed or bool(errors) or (args.strict and bool(warnings))

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
