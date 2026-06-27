# anything2md

一个把常见文档格式转换为 Markdown 的 Python 工具，并提供「电子书 → Markdown → 分类 → 书籍简介」的可选流水线。底层转换使用 [Pandoc](https://pandoc.org)，简介生成使用 Google Gemini API。

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
pip install -r requirements.txt
```

## 完整流水线（转换 → 归类 → 简介）

`pipeline.py` 是主入口：

```bash
python pipeline.py convert    # epubs/<分类>/ -> markdown/<分类>/
python pipeline.py organize   # 把已有 markdown/ 归位到与 epubs/ 一致的结构
python pipeline.py intros     # Gemini 读每本书 -> intros/<分类>/<书名>/
python pipeline.py all        # convert + organize + intros
```

### 分类由 epubs/ 文件夹决定

把电子书放进 `epubs/` 的子文件夹，同样的目录结构会镜像到 `markdown/` 和 `intros/`：

```
epubs/                  markdown/               intros/
├── Economics/          ├── Economics/          ├── Economics/
├── Religion/     -->   ├── Religion/     -->   ├── Religion/
└── ...                 └── ...                 └── ...
```

新增分类只需在 `epubs/` 下建文件夹，不需要改代码。

- 在 `epubs/` 根目录散放（未放入子文件夹）的书归到 `_uncategorized/`。
- `organize` 用于把已有的 Markdown 重新归位（例如旧版遗留文件），`--dry-run` 只预览不实际移动。
- 各分类对应的网站 `category` 与基础 `tags` 在 `anything2md/topics.py` 的 `FOLDER_META` 里配置；未配置的文件夹直接用文件夹名作 `category`。

### 书籍简介（intros）

对每本书：读取整本 Markdown → 连同提示词发给 Gemini → 解析结构化结果 → 在 `intros/<分类>/<书名>/` 下生成：

- `website.md`：带 Hugo frontmatter（title/slug/description/category/tags/date）的网站文章，可直接放进 Hugo 站点的 `content/posts/`。
- `generic.md`：不绑定平台的通用书评。
- `gemini_response.md`：模型原始返回，便于排查。

提示词要求模型只依据原书正文，输出约 1000 字的「核心内容 + 精彩部分」。

常用参数：

```bash
python pipeline.py intros --only 关键词   # 先跑一两本看效果
python pipeline.py intros --overwrite     # 强制重新生成已有的简介
```

超长的书（默认上限约 70 万字）会在送入模型前截断，控制台会标注「已截断」。

### 配置 Gemini key

把 `.env.example` 复制为 `.env` 并填入 key：

```bash
cp .env.example .env
```

`.env.example` 默认使用多 key 格式（配额耗尽时自动切换）：

```
GEMINI_API_KEY_1=第一个key
GEMINI_API_KEY_2=第二个key
# GEMINI_MODEL=gemini-2.5-flash   # 可选，默认 gemini-2.5-flash
```

只有一个 key 时，只填 `GEMINI_API_KEY_1` 即可。key 在 <https://aistudio.google.com/apikey> 免费获取，`.env` 已被 `.gitignore` 忽略，不会提交。

## 快速一键转换（VSCode）

打开 `epub2md.py`，在 VSCode 中点击 **▶ Run**，即可把 `epubs/` 下所有电子书转换到 `markdown/`，已转换的自动跳过。

打开 `docx2md.py` 同样运行，即可把 `docx/` 下所有 Word 文档转换到 `markdown/`。

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
| 5 | PDF | 实验性支持，优先级最低 |

## 支持的输入格式

| 扩展名 | Pandoc 格式 | 说明 |
|--------|-------------|------|
| `.epub` | epub | 书籍场景首选 |
| `.docx` | docx | 没有 EPUB 时优先 |
| `.html` / `.htm` | html | 可用备选 |
| `.odt` | odt | 可用备选 |
| `.rtf` | rtf | 结构质量不稳定 |
| `.txt` / `.md` | markdown | 结构较少 |
| `.pdf` | pdf | 实验性支持，优先级最低 |

文件名会自动 slugify：空格、方括号和特殊字符替换为下划线。

## 项目结构

```
anything2md/
├── pipeline.py          # 主入口（convert / organize / intros / all）
├── epub2md.py           # VSCode 一键运行（epubs/ -> markdown/）
├── docx2md.py           # VSCode 一键运行（docx/ -> markdown/）
├── convert.py           # 灵活 CLI（任意路径转换）
├── requirements.txt
├── .env.example
├── .gitignore
├── anything2md/         # 转换 + 归类
│   ├── cli.py           # convert.py 的参数解析
│   ├── converter.py     # 文件收集与调度
│   ├── pandoc_runner.py # pypandoc 封装
│   ├── formats.py       # 支持格式注册表
│   ├── topics.py        # 各 epubs 文件夹的 category / 基础 tags（可选）
│   ├── organize.py      # 把 markdown/ 归位到与 epubs/ 一致的结构
│   └── utils.py         # slugify、日志、pandoc 检查
└── md2intro/            # Gemini 书籍简介生成
    ├── config.py        # 提示词模板、字段定义、输入上限
    ├── gemini.py        # Gemini 客户端封装（支持多 key 轮换）
    ├── runner.py        # 调度（读书 → 调模型 → 写文件）
    ├── parse.py         # 解析结构化 @@字段 回答
    └── assemble.py      # 渲染网站版 + 通用版简介
```

运行时目录（均已在 `.gitignore` 忽略）：

- `epubs/`：源电子书，**文件夹结构即分类**
- `docx/`：源 Word 文档
- `markdown/`：转换结果，镜像 `epubs/`
- `intros/`：简介产物，镜像 `epubs/`
- `.env`：API key

## 许可证

代码采用 [MIT License](LICENSE)。

`epubs/`、`docx/`、`markdown/`、`intros/` 等目录已在 `.gitignore` 中默认忽略，不会提交到仓库。
