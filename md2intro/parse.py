"""Parse the structured ``@@FIELD`` answer Gemini returns."""

import re
from dataclasses import dataclass

from .config import FIELDS

_MARKER_RE = re.compile(r"^@@([A-Z]+)\s*$", re.MULTILINE)


class ParseError(Exception):
    pass


# Strip a leading heading the model sometimes repeats (e.g. it puts
# "### 精彩部分" at the top of the HIGHLIGHTS body, duplicating our section
# title). Only removes a heading whose text is exactly the section name.
_REDUNDANT_HEADING = re.compile(r"^\s*#{1,6}\s*(核心内容|精彩部分)\s*\n+")


def _strip_redundant_heading(body: str) -> str:
    return _REDUNDANT_HEADING.sub("", body, count=1).strip()


@dataclass
class Intro:
    title: str
    author: str
    slug: str
    description: str
    excerpt: str
    tags: list[str]
    core: str
    highlights: str


def parse(text: str) -> Intro:
    """Parse a structured answer block into an :class:`Intro`."""
    # Strip code fences if the model wrapped the whole block in ``` ... ```.
    text = re.sub(r"^```[a-zA-Z]*\n", "", text.strip())
    text = re.sub(r"\n```$", "", text)

    matches = list(_MARKER_RE.finditer(text))
    if not matches:
        raise ParseError("找不到 @@字段 标记，模型可能没按格式输出。")

    values: dict[str, str] = {}
    for i, m in enumerate(matches):
        name = m.group(1)
        if name == "END":
            break
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        values[name] = text[m.end():end].strip()

    missing = [f for f in FIELDS if not values.get(f)]
    if missing:
        raise ParseError(f"缺少字段：{', '.join(missing)}")

    tags = [t.strip() for t in re.split(r"[,，]", values["TAGS"]) if t.strip()]

    return Intro(
        title=values["TITLE"].strip(),
        author=values["AUTHOR"].strip(),
        slug=values["SLUG"].strip(),
        description=values["DESCRIPTION"].strip(),
        excerpt=values["EXCERPT"].strip(),
        tags=tags,
        core=_strip_redundant_heading(values["CORE"]),
        highlights=_strip_redundant_heading(values["HIGHLIGHTS"]),
    )
