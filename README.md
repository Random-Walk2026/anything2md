# doc2md

A simple Python CLI tool for converting EPUB, DOCX, HTML and other documents to Markdown using [Pandoc](https://pandoc.org).

For Chinese readers: see [README_CN.md](README_CN.md).

## Requirements

- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html)

### 1. Install Pandoc

| Platform | Command |
|----------|---------|
| macOS    | `brew install pandoc` |
| Ubuntu   | `sudo apt install pandoc` |
| Windows  | `winget install JohnMacFarlane.Pandoc` |

### 2. Install Python dependency

```bash
pip install pypandoc
```

## Quick start (one-click in VSCode)

Put your EPUB files inside an `epubs/` folder, then open `run.py` and click the **▶ Run** button in VSCode. Already-converted files are automatically skipped.

```
doc2md/
└── epubs/
    ├── category_a/
    │   └── book.epub
    └── book2.epub
```

Output:

```
markdown/
├── book.md
├── book_media/
│   └── images/
├── book2.md
└── book2_media/
```

## Input format priority

If you are choosing a source format on purpose, use them in this order:

1. `EPUB` — best default for books and long-form text. It usually preserves chapters, headings, paragraphs, and embedded images better than the other supported formats.
2. `DOCX` — strong choice for manually authored documents. Structure is often good, but book-like content is usually cleaner in EPUB.
3. `HTML` / `ODT` — workable when EPUB or DOCX is not available.
4. `RTF` / `TXT` / `MD` — usable, but structure quality depends heavily on the source.
5. `PDF` — lowest priority. It is supported as an experimental Pandoc input and may produce poor heading and paragraph structure.

Short version: if you have both `EPUB` and `PDF`, convert the `EPUB`.

## CLI usage

### Single file

```bash
python convert.py input.epub -o output_dir/
```

### Batch convert a directory

```bash
python convert.py epubs/ -o markdown/
```

### Recursive scan (subdirectories)

```bash
python convert.py epubs/ -o markdown/ --recursive
```

### Overwrite existing output

```bash
python convert.py epubs/ -o markdown/ --overwrite
```

### Force input format

```bash
python convert.py epubs/ -o markdown/ --from epub
```

### Specify output format

```bash
python convert.py epubs/ -o markdown/ --to gfm
```

### Disable media extraction

```bash
python convert.py epubs/ -o markdown/ --no-extract-media
```

### Verbose mode

```bash
python convert.py epubs/ -o markdown/ --verbose
```

## Supported formats

| Extension | Pandoc format | Notes |
|-----------|--------------|-------|
| `.epub`   | epub | recommended first choice for books |
| `.docx`   | docx | recommended when EPUB is unavailable |
| `.html` / `.htm` | html | acceptable fallback |
| `.odt`    | odt | acceptable fallback |
| `.rtf`    | rtf | structure quality varies |
| `.txt` / `.md` | markdown | minimal structure, depends on source formatting |
| `.pdf`    | pdf | experimental — lowest priority, may produce poor structure |

File names are automatically slugified: spaces, brackets, and special characters are replaced with underscores.

## Conversion summary

After a batch run, doc2md prints a summary:

```
Total:   10
Success: 8
Skipped: 1
Failed:  1
```

Skipped = output file already existed and `--overwrite` was not passed.  
Failed files are listed individually; the rest of the batch continues uninterrupted.

## Project structure

```
doc2md/
├── convert.py          # CLI entry point
├── run.py              # one-click VSCode runner (epubs/ -> markdown/)
├── requirements.txt
├── .gitignore
└── doc2md/
    ├── cli.py          # argument parsing
    ├── converter.py    # file collection and dispatch
    ├── pandoc_runner.py # pypandoc wrapper
    ├── formats.py      # supported format registry
    └── utils.py        # slugify, logging, pandoc check
```

## Reuse note

Code in this repository is released under the [MIT License](LICENSE).

If you repost project introductions, usage notes, or other non-code written materials from this repository, please keep a clear attribution to the original source.

Input directories (`epubs/`, `books/`, `input/`) and common document extensions are listed in `.gitignore` and will not be tracked by git.
