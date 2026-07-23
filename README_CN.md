# anything2md

一个把常见文档格式转换为干净、适合 LLM 使用的 Markdown 的 Python 工具。EPUB / DOCX / ODT 等使用 [Pandoc](https://pandoc.org) 转换；PDF 与 HTML 走微软开源的 [MarkItDown](https://github.com/microsoft/markitdown)——Pandoc 根本读不了 PDF，且对 CSS 排版的 HTML（页面 / 幻灯片）会残留大量 `<div>` 噪声，而 MarkItDown 会剥成纯文本。

英文说明见 [README.md](README.md)。

## 环境要求

- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html)（用于 EPUB/DOCX/ODT/RTF/TXT/MD；只处理 PDF/HTML 时不需要）

### 1. 安装 Pandoc

| 平台 | 命令 |
|------|------|
| macOS | `brew install pandoc` |
| Ubuntu | `sudo apt install pandoc` |
| Windows | `winget install JohnMacFarlane.Pandoc` |

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 批量流水线（转换 → 归类）

`pipeline.py` 是主入口：

```bash
python pipeline.py convert    # epubs/（Pandoc）+ pdfs/（MarkItDown）-> markdown/<分类>/
python pipeline.py organize   # 把已有 markdown/ 归位到与来源目录一致的结构
python pipeline.py all        # convert + organize
```

### 输出目录跟随来源目录

把文件放进 `epubs/` 或 `pdfs/` 的子文件夹，同样的目录结构会镜像到 `markdown/`：

```
epubs/Economics/book.epub  ──> markdown/Economics/book.md
pdfs/Reports/report.pdf    ──> markdown/Reports/report.md
```

新增分类只需在 `epubs/` 或 `pdfs/` 下建文件夹，不需要改代码。

- 在来源根目录散放（未放入子文件夹）的文件归到 `_uncategorized/`。
- `organize` 用于把已有的 Markdown 重新归位（例如旧版遗留文件），`--dry-run` 只预览不实际移动。

## 快速一键转换（VSCode）

打开 `epub2md.py`，在 VSCode 中点击 **▶ Run**，即可把 `epubs/` 下所有电子书转换到 `markdown/`，已转换的自动跳过。

打开 `docx2md.py` 同样运行，即可把 `docx/` 下所有 Word 文档转换到 `markdown/`。

打开 `pdf2md.py` 同样运行，即可把 `pdfs/` 下所有 PDF 通过 MarkItDown 转换到 `markdown/`。扫描版 / 纯图片 PDF 会被自动识别：默认跳过并给出警告（不会留下空的 `.md`）。要先做 OCR 见下。

### 扫描版 PDF 的 OCR（可选）

文本型 PDF 不需要额外依赖。扫描版 / 纯图片 PDF 加 `--ocr`，会先经 [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) + Tesseract 加一层文本层再转换：

```bash
python convert.py scanned.pdf -o out/ --ocr
python pipeline.py convert --ocr          # 对批量里的扫描件做 OCR
python convert.py scanned.pdf -o out/ --ocr --ocr-lang chi_tra+eng
```

OCR 是可选的系统级依赖（不在 `requirements.txt` 里）：

| 平台 | 命令 |
|------|------|
| macOS | `brew install ocrmypdf tesseract tesseract-lang` |
| Ubuntu | `sudo apt install ocrmypdf tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra` |

OCR 后的可搜索 PDF 会缓存在输出旁（`<slug>.ocr.pdf`），重跑时跳过重复 OCR。默认 OCR 语言：`chi_sim+chi_tra+eng`。

## 灵活 CLI（任意路径）

`convert.py` 提供完整的命令行界面，可转换任意路径的文件：

```bash
python convert.py input.epub -o output_dir/
python convert.py epubs/ -o markdown/ --recursive
python convert.py epubs/ -o markdown/ --overwrite
python convert.py epubs/ -o markdown/ --from epub --to gfm
python convert.py epubs/ -o markdown/ --no-extract-media
python convert.py epubs/ -o markdown/ --verbose
```

## 推荐输入格式

| 优先级 | 格式 | 说明 |
|--------|------|------|
| 1 | EPUB | 书籍场景首选，结构保留最完整 |
| 2 | DOCX | 人工整理的文档优先考虑 |
| 3 | HTML / ODT | 可用备选 |
| 4 | RTF / TXT / MD | 结构质量依赖原始文件 |
| 5 | PDF | 走 MarkItDown；可复制文字的 PDF 效果好，扫描件需先 OCR |

## 支持的输入格式

| 扩展名 | 转换引擎 | 说明 |
|--------|----------|------|
| `.epub` | pandoc（epub） | 书籍场景首选 |
| `.docx` | pandoc（docx） | 没有 EPUB 时优先 |
| `.html` / `.htm` | MarkItDown | 剥掉 CSS/排版噪声；页面、幻灯片首选 |
| `.odt` | pandoc（odt） | 可用备选 |
| `.rtf` | pandoc（rtf） | 结构质量不稳定 |
| `.txt` / `.md` | pandoc（markdown） | 结构较少 |
| `.pdf` | MarkItDown（+ 可选 OCRmyPDF） | 可复制文字的 PDF 效果好；扫描件自动识别，加 `--ocr` 走 OCR |

文件名会自动 slugify：空格、方括号和特殊字符替换为下划线。

## 项目结构

```
anything2md/
├── pipeline.py          # 批量入口（convert / organize / all）
├── epub2md.py           # VSCode 一键运行（epubs/ -> markdown/）
├── docx2md.py           # VSCode 一键运行（docx/ -> markdown/）
├── pdf2md.py            # VSCode 一键运行（pdfs/ -> markdown/，走 MarkItDown）
├── convert.py           # 灵活 CLI（任意路径转换）
├── requirements.txt
├── .gitignore
├── anything2md/         # 转换 + 归类
│   ├── cli.py           # convert.py 的参数解析
│   ├── converter.py     # 文件收集与调度（pandoc / MarkItDown 分流）
│   ├── pandoc_runner.py # pypandoc 封装
│   ├── markitdown_runner.py # MarkItDown 封装（PDF / HTML）
│   ├── scan_detector.py # 识别扫描版 / 纯图片 PDF
│   ├── ocr_runner.py    # OCRmyPDF 封装（可选，处理扫描件）
│   ├── formats.py       # 支持格式注册表
│   ├── organize.py      # 把 markdown/ 归位到与来源目录一致的结构
│   └── utils.py         # slugify、日志、pandoc 检查
└── scripts/
    └── check_markdown.py # 轻量 Markdown 输出质检
```

运行时目录（均已在 `.gitignore` 忽略）：

- `epubs/`：源电子书，**文件夹结构即分类**
- `docx/`：源 Word 文档
- `pdfs/`：源 PDF（通过 MarkItDown 转换）
- `markdown/`：转换结果，镜像来源目录

## 许可证

代码采用 [MIT License](LICENSE)。

`epubs/`、`docx/`、`pdfs/`、`markdown/` 等目录已在 `.gitignore` 中默认忽略，不会提交到仓库。
