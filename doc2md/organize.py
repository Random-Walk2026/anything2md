"""Keep ``markdown/`` foldered the same way as ``epubs/``.

``convert`` already mirrors the source layout for freshly converted books. This
module re-files *existing* Markdown (e.g. books converted before this layout, or
left at the root) so every book sits under ``markdown/<epubs-folder>/``. The
mapping is derived from ``epubs/`` by slugifying each source filename, so it
matches the converter's output names exactly.
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .formats import SUPPORTED_INPUT_FORMATS
from .topics import UNCATEGORIZED
from .utils import slugify


@dataclass
class OrganizeSummary:
    moved: int = 0
    skipped: int = 0
    uncategorized: list[str] = field(default_factory=list)
    moves: list[tuple[str, str]] = field(default_factory=list)  # (stem, folder)

    def print(self) -> None:
        for stem, folder in self.moves:
            print(f"  {folder}/  <-  {stem}")
        print(f"\nMoved:         {self.moved}")
        print(f"Already filed: {self.skipped}")
        if self.uncategorized:
            print(f"\nUncategorized ({len(self.uncategorized)}) -> {UNCATEGORIZED}/:")
            for stem in self.uncategorized:
                print(f"  {stem}")
            print("These have no matching source folder under epubs/.")


def slug_to_folder(epubs_dir: Path) -> dict[str, str]:
    """Map each book's slug -> its top-level folder name under epubs/."""
    mapping: dict[str, str] = {}
    if not epubs_dir.is_dir():
        return mapping
    for src in epubs_dir.rglob("*"):
        if not src.is_file() or src.suffix.lower() not in SUPPORTED_INPUT_FORMATS:
            continue
        rel = src.parent.relative_to(epubs_dir)
        folder = rel.parts[0] if rel.parts else ""
        if folder:  # ignore loose files at the epubs root
            mapping[slugify(src.stem)] = folder
    return mapping


def organize(markdown_dir: Path, epubs_dir: Path, dry_run: bool = False) -> OrganizeSummary:
    summary = OrganizeSummary()
    mapping = slug_to_folder(epubs_dir)

    # Every markdown file currently anywhere under markdown_dir.
    for md in sorted(markdown_dir.rglob("*.md")):
        stem = md.stem
        folder = mapping.get(stem, UNCATEGORIZED)
        if folder == UNCATEGORIZED:
            summary.uncategorized.append(stem)

        dest_dir = markdown_dir / folder
        dest_md = dest_dir / md.name

        if md.parent == dest_dir:
            summary.skipped += 1
            continue
        if dest_md.exists():
            print(f"Skip (target exists): {folder}/{md.name}")
            summary.skipped += 1
            continue

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(md), str(dest_md))
            media = md.parent / f"{stem}_media"
            if media.is_dir():
                shutil.move(str(media), str(dest_dir / media.name))

        summary.moved += 1
        summary.moves.append((stem, folder))

    if not dry_run:
        _prune_empty_dirs(markdown_dir)

    summary.print()
    return summary


def _prune_empty_dirs(root: Path) -> None:
    for d in sorted(root.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def iter_books(markdown_dir: Path):
    """Yield (folder, md_path) for every book under a category folder."""
    for folder_dir in sorted(markdown_dir.iterdir()):
        if not folder_dir.is_dir() or folder_dir.name.endswith("_media"):
            continue
        for md in sorted(folder_dir.glob("*.md")):
            yield folder_dir.name, md
