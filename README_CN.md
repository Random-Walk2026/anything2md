# doc2md

一个基于 [Pandoc](https://pandoc.org) 的 Python 命令行工具，用于把 EPUB、DOCX、HTML 等文档转换为 Markdown。

英文说明见 [README.md](README.md)。

## 环境要求

- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html)

### 1. 安装 Pandoc

| 平台 | 命令 |
|------|------|
| macOS | `brew install pandoc` |
| Ubuntu | `sudo apt install pandoc` |
| Windows | `winget install JohnMacFarlane.Pandoc` |

### 2. 安装 Python 依赖

```bash
pip install pypandoc
```

## 最推荐的输入格式

如果你可以自己选择源文件格式，建议按下面的优先级使用：

1. `EPUB`
   适合书籍和长文本，通常最能保留章节、标题、段落和图片结构，是本项目的首选格式。
2. `DOCX`
   适合人工整理过的文档；如果同时有 EPUB，一般还是优先 EPUB。
3. `HTML` / `ODT`
   可以正常使用，适合作为备选输入。
4. `RTF` / `TXT` / `MD`
   能转，但结构质量更依赖原始文件本身。
5. `PDF`
   优先级最低。当前通过 Pandoc 实验性支持，常见问题是标题层级、段落切分和整体结构较差。

一句话总结：如果你同时有 `EPUB` 和 `PDF`，优先转换 `EPUB`。

## 快速开始（VSCode 一键运行）

把 EPUB 文件放进 `epubs/` 目录，然后打开 `run.py`，在 VSCode 中点击 **▶ Run**。已经转换过的文件会自动跳过。

```text
doc2md/
└── epubs/
    ├── category_a/
    │   └── book.epub
    └── book2.epub
```

输出目录示例：

```text
markdown/
├── book.md
├── book_media/
│   └── images/
├── book2.md
└── book2_media/
```

## 命令行用法

### 转换单个文件

```bash
python convert.py input.epub -o output_dir/
```

### 批量转换目录

```bash
python convert.py epubs/ -o markdown/
```

### 递归扫描子目录

```bash
python convert.py epubs/ -o markdown/ --recursive
```

### 覆盖已存在输出

```bash
python convert.py epubs/ -o markdown/ --overwrite
```

### 强制指定输入格式

```bash
python convert.py epubs/ -o markdown/ --from epub
```

### 指定输出格式

```bash
python convert.py epubs/ -o markdown/ --to gfm
```

### 禁用媒体提取

```bash
python convert.py epubs/ -o markdown/ --no-extract-media
```

### 显示详细日志

```bash
python convert.py epubs/ -o markdown/ --verbose
```

## 支持的输入格式

| 扩展名 | Pandoc 格式 | 说明 |
|--------|-------------|------|
| `.epub` | epub | 书籍场景首选 |
| `.docx` | docx | 没有 EPUB 时优先考虑 |
| `.html` / `.htm` | html | 可用备选 |
| `.odt` | odt | 可用备选 |
| `.rtf` | rtf | 结构质量不稳定 |
| `.txt` / `.md` | markdown | 结构较少，效果依赖源文件 |
| `.pdf` | pdf | 实验性支持，优先级最低 |

文件名会自动做 slugify 处理：空格、方括号和特殊字符会被替换为下划线，便于生成稳定的 Markdown 文件名。

## 转换结果汇总

批量运行后，doc2md 会输出一份摘要：

```text
Total:   10
Success: 8
Skipped: 1
Failed:  1
```

其中：

- `Skipped` 表示目标文件已存在，且没有传入 `--overwrite`
- `Failed` 会逐个列出失败文件，但不会中断整批任务

## 项目结构

```text
doc2md/
├── convert.py           # CLI 入口
├── run.py               # VSCode 一键运行入口（epubs/ -> markdown/）
├── requirements.txt
├── .gitignore
└── doc2md/
    ├── cli.py           # 参数解析
    ├── converter.py     # 文件收集与调度
    ├── pandoc_runner.py # pypandoc 封装
    ├── formats.py       # 支持格式注册表
    └── utils.py         # slugify、日志、pandoc 检查
```

## 复用说明

本仓库代码采用 [MIT License](LICENSE)。

如果转载本仓库的项目介绍、使用说明或其他非代码文字内容，请注明原始出处。

`epubs/`、`books/`、`input/`、`markdown/` 等目录已经在 `.gitignore` 中默认忽略，不会作为本地资料提交到仓库。
