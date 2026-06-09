"""Generate book intros end-to-end with Gemini.

For each organized book: read its Markdown, send it to Gemini with the
universal prompt, parse the structured answer, and write a Hugo website
article plus a generic intro.
"""

from pathlib import Path

from doc2md.organize import iter_books
from .assemble import render_generic, render_website
from .config import GENERIC_FILE, MAX_INPUT_CHARS, RAW_FILE, WEBSITE_FILE
from .gemini import GeminiError, generate_intro, get_clients, model_name
from .parse import ParseError, parse


def generate_intros(
    markdown_dir: Path,
    intros_dir: Path,
    overwrite: bool = False,
    only: str | None = None,
) -> None:
    """Loop over books and produce website.md + generic.md for each.

    `only` optionally filters to books whose stem contains the substring.
    """
    try:
        clients = get_clients()
    except GeminiError as exc:
        print(exc)
        return

    print(f"使用模型：{model_name()}\n")

    done = skipped = failed = 0

    for topic, md in iter_books(markdown_dir):
        if only and only not in md.stem:
            continue

        work = intros_dir / topic / md.stem
        website_path = work / WEBSITE_FILE
        if website_path.exists() and not overwrite:
            skipped += 1
            continue

        book_text = md.read_text(encoding="utf-8")
        trunc = "（已截断）" if len(book_text) > MAX_INPUT_CHARS else ""
        print(f"→ [{topic}] {md.stem}  {len(book_text):,} 字{trunc}")

        try:
            raw = generate_intro(clients, book_text, md.stem)
        except GeminiError as exc:
            print(f"  失败：{exc}")
            failed += 1
            continue

        work.mkdir(parents=True, exist_ok=True)
        (work / RAW_FILE).write_text(raw, encoding="utf-8")

        try:
            intro = parse(raw)
        except ParseError as exc:
            print(f"  解析失败：{exc}（原始响应已存到 {RAW_FILE}）")
            failed += 1
            continue

        website_path.write_text(render_website(intro, topic), encoding="utf-8")
        (work / GENERIC_FILE).write_text(
            render_generic(intro, topic), encoding="utf-8"
        )
        done += 1
        print(f"  OK  {intro.title}")
        print(f"      网站版: {website_path}")
        print(f"      通用版: {work / GENERIC_FILE}")

    print(f"\n生成: {done}    跳过(已存在): {skipped}    失败: {failed}")
