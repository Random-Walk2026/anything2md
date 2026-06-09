"""Render parsed intros into a website article and a generic intro."""

from datetime import date

from doc2md.topics import folder_meta
from .parse import Intro


def _yq(value: str) -> str:
    """Quote a scalar for YAML frontmatter."""
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _merge_tags(intro_tags: list[str], base_tags: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for t in [*intro_tags, *base_tags]:
        seen.setdefault(t, None)
    return list(seen)


def render_website(intro: Intro, folder: str, on: date | None = None) -> str:
    """Hugo article: frontmatter + structured body, ready for content/posts/."""
    meta = folder_meta(folder)
    today = (on or date.today()).isoformat()
    tags = _merge_tags(intro.tags, meta.tags)
    tags_yaml = "[" + ", ".join(_yq(t) for t in tags) + "]"

    frontmatter = "\n".join([
        "---",
        f"title: {_yq(intro.title)}",
        f"slug: {_yq(intro.slug)}",
        f"description: {_yq(intro.description)}",
        f"excerpt: {_yq(intro.excerpt)}",
        f"category: {_yq(meta.category)}",
        f"tags: {tags_yaml}",
        f'date: "{today}"',
        "draft: false",
        "---",
    ])

    body = "\n".join([
        "",
        f"# {intro.title}",
        "",
        "## 核心内容",
        "",
        intro.core,
        "",
        "## 精彩部分",
        "",
        intro.highlights,
        "",
    ])
    return frontmatter + "\n" + body


def render_generic(intro: Intro, folder: str) -> str:
    """Platform-agnostic intro for reposting anywhere."""
    author = intro.author or "佚名"
    return "\n".join([
        f"# {intro.title}",
        "",
        f"> 作者：{author}　｜　分类：{folder}",
        "",
        intro.description,
        "",
        "## 核心内容",
        "",
        intro.core,
        "",
        "## 精彩部分",
        "",
        intro.highlights,
        "",
        "---",
        "",
        "*本简介依据原书整理生成，仅供参考，不代表书中全部内容。*",
        "",
    ])
