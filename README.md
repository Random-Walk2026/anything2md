# doc2md

A simple Python CLI tool for converting EPUB, DOCX, HTML and other documents to Markdown using [Pandoc](https://pandoc.org).

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
| `.epub`   | epub | |
| `.docx`   | docx | |
| `.html` / `.htm` | html | |
| `.odt`    | odt | |
| `.rtf`    | rtf | |
| `.txt` / `.md` | markdown | |
| `.pdf`    | pdf | experimental — may produce poor structure |

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

## Legal notice

> Do not commit copyrighted EPUB, PDF, or DOCX files to this repository.  
> Input directories (`epubs/`, `books/`, `input/`) and common document extensions are listed in `.gitignore` and will not be tracked by git.
