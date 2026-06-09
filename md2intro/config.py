"""Field markers, output filenames and the universal intro prompt (Gemini)."""

# Field markers in the structured answer Gemini returns. Each marker sits on
# its own line; everything until the next marker is that field's value.
FIELDS = [
    "TITLE",
    "AUTHOR",
    "SLUG",
    "DESCRIPTION",
    "EXCERPT",
    "TAGS",
    "CORE",
    "HIGHLIGHTS",
]

# Output filenames inside each per-book working folder under intros/.
RAW_FILE = "gemini_response.md"   # raw model output, kept for inspection/debug
WEBSITE_FILE = "website.md"       # Hugo article
GENERIC_FILE = "generic.md"       # platform-agnostic intro

# Upper bound on book characters sent to Gemini. Gemini 2.5 accepts ~1M input
# tokens; for CJK text that is well under 1M characters, so we cap here and
# truncate longer books (with a note appended to the prompt).
MAX_INPUT_CHARS = 700_000

# The universal prompt. The book's full text is appended after it.
# `{title_hint}` is the book's filename, only as a gentle hint.
PROMPT_TEMPLATE = """你是我的中文图书编辑与内容写手。下面会给你一本书的正文（文件名参考：{title_hint}）。请你**只依据给你的正文**，为它写一篇用于网络发布的「书籍简介」。

写作要求：
1. 只依据给你的正文，不要编造书里没有的内容；不确定的信息用「书中提到」「大致可理解为」等谨慎措辞，或直接省略，不要硬写。
2. 用清楚、自然的中文，避免营销腔、夸张的标题党，以及明显的 AI 套话。
3. 客观介绍：既不过度吹捧，也不简单贬低，定位为「值得了解的一本书」。
4. 引用书中原文、观点或案例时以原文为准，可用 Markdown 引用块 `>`。
5. 「核心内容」说明这本书讲什么、主要观点或整体结构；「精彩部分」挑 2–4 个最有价值或最有意思的点。
6. 篇幅要求：「核心内容」+「精彩部分」中**你自己撰写的介绍文字合计不少于 1000 字**（建议 1100–1500 字）；引用书中原文的部分不计入这 1000 字，请在写够介绍文字的基础上再适当引用，不要用大段引用来凑字数。

**输出格式（极重要）**：严格按下面的结构输出。每个字段以 `@@字段名` 独占一行开头，字段内容紧跟在下一行开始；除了这个结构本身，不要输出任何前言、说明或结语。

@@TITLE
《书名》简介：一句话定位（整行不超过 30 字）
@@AUTHOR
作者（多位用、号分隔；不确定写「佚名」或「题为某某」）
@@SLUG
book-书名拼音或英文缩写（全部小写，单词间用连字符 -）
@@DESCRIPTION
SEO 描述，1–2 句话，不超过 70 字
@@EXCERPT
文章卡片摘要，可与 description 相同或略短
@@TAGS
3–8 个标签，用英文逗号 , 分隔
@@CORE
（这里写核心内容正文，可分多段，可用 `### 小标题`）
@@HIGHLIGHTS
（这里写精彩部分正文，2–4 个要点，可用 `>` 引用书中原文）
@@END
"""
