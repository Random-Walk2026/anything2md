"""Thin wrapper around the Gemini API for generating book intros.

Reads ``GEMINI_API_KEY`` (or ``GEMINI_API_KEY_1`` / ``_2`` / … for multiple
keys) from the environment or a ``.env`` file.  When multiple keys are
provided the client list is cycled on rate-limit (429 / RESOURCE_EXHAUSTED)
errors, with up to 3 full rounds before giving up.
"""

import os
import time

from .config import MAX_INPUT_CHARS, PROMPT_TEMPLATE

DEFAULT_MODEL = "gemini-3.5-flash"


class GeminiError(Exception):
    pass


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _load_keys() -> list[str]:
    keys: list[str] = []
    i = 1
    while True:
        k = os.environ.get(f"GEMINI_API_KEY_{i}", "").strip()
        if not k:
            break
        keys.append(k)
        i += 1
    if not keys:
        single = os.environ.get("GEMINI_API_KEY", "").strip()
        if single:
            keys.append(single)
    return keys


def model_name() -> str:
    return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def get_clients() -> list:
    """Return a list of Gemini clients (one per API key), raising GeminiError if none found."""
    _load_env()
    keys = _load_keys()
    if not keys:
        raise GeminiError(
            "未找到 Gemini API key。请在项目根目录的 .env 中设置：\n"
            "  GEMINI_API_KEY=你的key\n"
            "多个 key 可用 GEMINI_API_KEY_1 / GEMINI_API_KEY_2 … 依次设置。\n"
            "key 可在 https://aistudio.google.com/apikey 免费获取。"
        )
    try:
        from google import genai
    except ImportError:
        raise GeminiError(
            "缺少依赖，请先安装：pip install google-genai python-dotenv"
        )
    return [genai.Client(api_key=k) for k in keys]


def generate_intro(clients: list, book_text: str, title_hint: str) -> str:
    """Send one book to Gemini (with multi-key rotation) and return the raw structured answer."""
    from google.genai import types

    prompt = PROMPT_TEMPLATE.format(title_hint=title_hint)
    truncated = book_text[:MAX_INPUT_CHARS]
    note = (
        ""
        if len(book_text) <= MAX_INPUT_CHARS
        else "\n\n（注：因篇幅限制，以上仅为本书前一部分正文，请据此尽量概括全书。）"
    )
    contents = (
        f"{prompt}\n\n=== 书籍正文开始 ===\n{truncated}\n=== 书籍正文结束 ==={note}"
    )
    config = types.GenerateContentConfig(max_output_tokens=8192)

    MAX_ROUNDS = 3
    n = len(clients)
    last_exc: Exception | None = None

    for round_num in range(1, MAX_ROUNDS + 1):
        all_rate_limited = True
        for idx, client in enumerate(clients):
            label = f"key {idx + 1}/{n}"
            try:
                parts: list[str] = []
                for chunk in client.models.generate_content_stream(
                    model=model_name(), contents=contents, config=config
                ):
                    if getattr(chunk, "text", None):
                        parts.append(chunk.text)
                text = "".join(parts).strip()
                if not text:
                    raise GeminiError("Gemini 返回了空响应（可能触发了安全过滤或配额限制）。")
                return text
            except GeminiError:
                raise
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                is_rate_limit = any(s in msg for s in ("429", "resource_exhausted", "quota"))
                is_transient = is_rate_limit or any(s in msg for s in (
                    "503", "500", "unavailable", "disconnect", "deadline",
                    "timeout", "timed out", "connection", "internal", "try again",
                ))
                if not is_transient:
                    raise GeminiError(f"调用 Gemini 失败：{exc}") from exc
                if is_rate_limit:
                    if idx + 1 < n:
                        print(f"  {label} 配额限制，切换下一个 key…")
                else:
                    all_rate_limited = False
                    wait = 5 * round_num
                    print(f"  {label} 暂时不可用，{wait}s 后重试…")
                    time.sleep(wait)

        if round_num < MAX_ROUNDS:
            wait = 60 * round_num if all_rate_limited else 15 * round_num
            reason = "所有 key 配额耗尽" if all_rate_limited else "所有 key 暂时不可用"
            print(f"  {reason}（第 {round_num} 轮），等待 {wait}s 后重试…")
            time.sleep(wait)

    raise GeminiError(f"调用 Gemini 失败（已重试 {MAX_ROUNDS} 轮）：{last_exc}")
