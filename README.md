# anything2md

A Python toolkit for converting common document formats to clean, LLM-friendly Markdown.

EPUB / DOCX / ODT and friends go through [Pandoc](https://pandoc.org); PDF and HTML are routed through Microsoft [MarkItDown](https://github.com/microsoft/markitdown), which produces cleaner, LLM-friendly Markdown — Pandoc cannot read PDF at all, and on CSS-heavy HTML (pages / slide decks) it leaves raw `<div>` markup, whereas MarkItDown strips it to plain text.

For Chinese readers: see [README_CN.md](README_CN.md).

## Requirements

- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html) (for EPUB/DOCX/ODT/RTF/TXT/MD — not needed for PDF/HTML-only use)

### 1. Install Pandoc

| Platform | Command |
|----------|---------|
| macOS    | `brew install pandoc` |
| Ubuntu   | `sudo apt install pandoc` |
| Windows  | `winget install JohnMacFarlane.Pandoc` |

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

## Batch pipeline (convert → organise)

`pipeline.py` is the main entry point:

```bash
python pipeline.py convert    # epubs/ (pandoc) + pdfs/ (MarkItDown) -> markdown/<Folder>/
python pipeline.py organize   # re-file markdown/ to mirror source-folder structure
python pipeline.py all        # convert + organize
```

### Folder structure follows the source

Put files into sub-folders under `epubs/` or `pdfs/`; the same structure is mirrored to `markdown/`:

```
epubs/Economics/book.epub  ──> markdown/Economics/book.md
pdfs/Reports/report.pdf    ──> markdown/Reports/report.md
```

No code changes are needed to add a new category—just create the folder. The
`organize` command is mainly for older Markdown files that predate mirrored
output; `--dry-run` previews moves without changing files.

## Quick one-click conversion (VSCode)

Open `epub2md.py` and click **▶ Run** in VSCode to convert everything in `epubs/` to `markdown/`. Already-converted files are skipped automatically.

Open `docx2md.py` the same way to convert everything in `docx/` to `markdown/`.

Open `pdf2md.py` the same way to convert everything in `pdfs/` to `markdown/` via MarkItDown. Scanned/image-only PDFs are detected automatically: by default they are skipped with a warning (no empty `.md` is written). To OCR them first, see below.

### OCR for scanned PDFs (optional)

Text PDFs need nothing extra. For scanned/image-only PDFs, pass `--ocr` to run them through [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) + Tesseract before conversion:

```bash
python convert.py scanned.pdf -o out/ --ocr
python pipeline.py convert --ocr          # OCR scanned PDFs in the batch
python convert.py scanned.pdf -o out/ --ocr --ocr-lang chi_tra+eng
```

OCR is an optional, system-level dependency (not installed by `requirements.txt`):

| Platform | Command |
|----------|---------|
| macOS    | `brew install ocrmypdf tesseract tesseract-lang` |
| Ubuntu   | `sudo apt install ocrmypdf tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra` |

The OCR'd searchable PDF is cached next to the output (`<slug>.ocr.pdf`), so re-runs skip re-OCR. Default OCR languages: `chi_sim+chi_tra+eng`.

## Flexible CLI (any path)

`convert.py` exposes a full CLI for converting arbitrary files or directories:

```bash
python convert.py input.epub -o output_dir/
python convert.py epubs/ -o markdown/ --recursive
python convert.py epubs/ -o markdown/ --overwrite
python convert.py epubs/ -o markdown/ --from epub --to gfm
python convert.py epubs/ -o markdown/ --no-extract-media
python convert.py epubs/ -o markdown/ --verbose
```

## Input format priority

| Priority | Format | Notes |
|----------|--------|-------|
| 1 | EPUB | best default for books |
| 2 | DOCX | good for authored documents |
| 3 | HTML / ODT | acceptable fallback |
| 4 | RTF / TXT / MD | structure quality varies |
| 5 | PDF | via MarkItDown; text PDFs good, scanned PDFs need OCR |

## Supported formats

| Extension | Engine | Notes |
|-----------|--------|-------|
| `.epub`   | pandoc (epub) | recommended first choice for books |
| `.docx`   | pandoc (docx) | recommended when EPUB is unavailable |
| `.html` / `.htm` | MarkItDown | strips CSS/layout noise; best for pages & slide decks |
| `.odt`    | pandoc (odt) | acceptable fallback |
| `.rtf`    | pandoc (rtf) | structure quality varies |
| `.txt` / `.md` | pandoc (markdown) | minimal structure |
| `.pdf`    | MarkItDown (+ optional OCRmyPDF) | clean text from copyable PDFs; scanned PDFs auto-detected, OCR'd with `--ocr` |

File names are automatically slugified (spaces and special characters → underscores).

## Project structure

```
anything2md/
├── pipeline.py          # batch entry point (convert / organize / all)
├── epub2md.py           # one-click VSCode runner (epubs/ -> markdown/)
├── docx2md.py           # one-click VSCode runner (docx/ -> markdown/)
├── pdf2md.py            # one-click VSCode runner (pdfs/ -> markdown/ via MarkItDown)
├── convert.py           # flexible CLI for arbitrary paths
├── requirements.txt
├── .gitignore
├── anything2md/         # conversion + organisation
│   ├── cli.py           # argument parsing for convert.py
│   ├── converter.py     # file collection and dispatch (pandoc vs MarkItDown)
│   ├── pandoc_runner.py # pypandoc wrapper
│   ├── markitdown_runner.py # MarkItDown wrapper (PDF / HTML)
│   ├── scan_detector.py # detect scanned/image-only PDFs
│   ├── ocr_runner.py    # OCRmyPDF wrapper (optional, for scanned PDFs)
│   ├── formats.py       # supported format registry
│   ├── organize.py      # re-files markdown/ to mirror source folders
│   └── utils.py         # slugify, logging, pandoc check
└── scripts/
    └── check_markdown.py # lightweight Markdown output QA
```

Runtime directories (all git-ignored):

- `epubs/` — source e-books; folder structure defines categories
- `docx/` — source Word documents
- `pdfs/` — source PDFs (converted via MarkItDown)
- `markdown/` — converted output, mirrors source folders

## License

Code in this repository is released under the [MIT License](LICENSE).

Input directories (`epubs/`, `docx/`, `pdfs/`, `markdown/`) and common document extensions are listed in `.gitignore` and will not be tracked by git.
