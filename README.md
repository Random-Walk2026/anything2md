# doc2md

A Python pipeline for converting EPUB / DOCX / HTML files to Markdown and automatically generating book introductions via Google Gemini.

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

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

## Full pipeline (convert → organise → intro)

`pipeline.py` is the main entry point:

```bash
python pipeline.py convert    # epubs/<Folder>/ -> markdown/<Folder>/
python pipeline.py organize   # re-file markdown/ to mirror epubs/ structure
python pipeline.py intros     # Gemini reads each book -> intros/<Folder>/<book>/
python pipeline.py all        # convert + organize + intros
```

### Categorisation follows your epubs/ folders

Put books into sub-folders under `epubs/`; the same structure is mirrored to `markdown/` and `intros/`:

```
epubs/                  markdown/               intros/
├── Economics/          ├── Economics/          ├── Economics/
├── Religion/     -->   ├── Religion/     -->   ├── Religion/
└── ...                 └── ...                 └── ...
```

No code changes needed to add a new category — just create the folder.

### Book introductions (Gemini)

For each book, `intros` reads the full Markdown, sends it to Gemini with a structured prompt, and writes two files:

- `website.md` — Hugo article with frontmatter (title / slug / description / category / tags / date)
- `generic.md` — platform-agnostic intro

Useful flags:

```bash
python pipeline.py intros --only KEYWORD   # test on one book first
python pipeline.py intros --overwrite      # regenerate existing intros
```

### Gemini API key

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

`.env.example` uses the multi-key format (automatic rotation on rate-limit):

```
GEMINI_API_KEY_1=your_first_key
GEMINI_API_KEY_2=your_second_key
# GEMINI_MODEL=gemini-2.5-flash   # optional, defaults to gemini-2.5-flash
```

A single key also works — just set `GEMINI_API_KEY_1` alone. Get free keys at <https://aistudio.google.com/apikey>. `.env` is git-ignored.

## Quick one-click conversion (VSCode)

Open `epub2md.py` and click **▶ Run** in VSCode to convert everything in `epubs/` to `markdown/`. Already-converted files are skipped automatically.

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
| 5 | PDF | experimental, often poor structure |

## Supported formats

| Extension | Pandoc format | Notes |
|-----------|--------------|-------|
| `.epub`   | epub | recommended first choice for books |
| `.docx`   | docx | recommended when EPUB is unavailable |
| `.html` / `.htm` | html | acceptable fallback |
| `.odt`    | odt | acceptable fallback |
| `.rtf`    | rtf | structure quality varies |
| `.txt` / `.md` | markdown | minimal structure |
| `.pdf`    | pdf | experimental — lowest priority |

File names are automatically slugified (spaces and special characters → underscores).

## Project structure

```
doc2md/
├── pipeline.py          # main entry point (convert / organize / intros / all)
├── epub2md.py           # one-click VSCode runner (epubs/ -> markdown/)
├── convert.py           # flexible CLI for arbitrary paths
├── requirements.txt
├── .env.example
├── .gitignore
├── doc2md/              # conversion + organisation
│   ├── cli.py           # argument parsing for convert.py
│   ├── converter.py     # file collection and dispatch
│   ├── pandoc_runner.py # pypandoc wrapper
│   ├── formats.py       # supported format registry
│   ├── topics.py        # optional category/tag metadata per epubs/ folder
│   ├── organize.py      # re-files markdown/ to mirror epubs/ structure
│   └── utils.py         # slugify, logging, pandoc check
└── md2intro/            # Gemini book-intro generation
    ├── config.py        # prompt template, field definitions, input limit
    ├── gemini.py        # Gemini client with multi-key rotation
    ├── runner.py        # intro scheduler (read → call model → write)
    ├── parse.py         # parse structured @@FIELD response
    └── assemble.py      # render website + generic intros
```

Runtime directories (all git-ignored):

- `epubs/` — source e-books; folder structure defines categories
- `markdown/` — converted output, mirrors `epubs/`
- `intros/` — generated intros, mirrors `epubs/`
- `.env` — API keys

## License

Code in this repository is released under the [MIT License](LICENSE).

Input directories (`epubs/`, `markdown/`, `intros/`) and common document extensions are listed in `.gitignore` and will not be tracked by git.
