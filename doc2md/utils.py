import re
import sys
from pathlib import Path


def check_pandoc() -> None:
    try:
        import pypandoc
        pypandoc.get_pandoc_version()
    except OSError:
        print(
            "Error: pandoc is not installed or not in PATH.\n"
            "Install it from: https://pandoc.org/installing.html\n"
            "  macOS:   brew install pandoc\n"
            "  Ubuntu:  sudo apt install pandoc\n"
            "  Windows: winget install JohnMacFarlane.Pandoc",
            file=sys.stderr,
        )
        sys.exit(1)


def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "_", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-_")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)
