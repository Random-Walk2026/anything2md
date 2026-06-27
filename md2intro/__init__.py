"""md2intro — Gemini-powered book-intro generation for anything2md.

For each organized book under ``markdown/<topic>/``, Gemini reads the full
text and returns a structured ``@@FIELD`` block, which is rendered into:

  - ``intros/<topic>/<book>/website.md`` — Hugo article (frontmatter + body)
  - ``intros/<topic>/<book>/generic.md`` — platform-agnostic intro

Requires ``GEMINI_API_KEY`` (see ``.env``). Run via ``python pipeline.py intros``.
"""
