import re

# теги которые понимает телега
_ALLOWED_TAGS = re.compile(r"</?(?:b|i|u|s|code|pre|a(?:\s[^>]*)?)>")


def md_to_html(text: str) -> str:
    """Конвертируем md/html из ответа LLM в телеграм-html.

    Модель может вернуть и html-теги, и маркдаун - обрабатываем оба варианта.
    """
    # вырезаем допустимые теги, запоминая позиции
    parts = []
    last = 0
    for m in _ALLOWED_TAGS.finditer(text):
        if m.start() > last:
            parts.append(("text", text[last:m.start()]))
        parts.append(("tag", m.group()))
        last = m.end()
    if last < len(text):
        parts.append(("text", text[last:]))

    result = []
    for kind, chunk in parts:
        if kind == "tag":
            result.append(chunk)
        else:
            chunk = chunk.replace("&", "&amp;")
            chunk = chunk.replace("<", "&lt;")
            chunk = chunk.replace(">", "&gt;")

            # ```блоки кода``` -> <pre>
            chunk = re.sub(
                r"```(?:\w*\n)?(.*?)```",
                lambda m: f"<pre>{m.group(1).strip()}</pre>",
                chunk,
                flags=re.DOTALL,
            )
            chunk = re.sub(r"`([^`]+)`", r"<code>\1</code>", chunk)
            chunk = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", chunk)
            chunk = re.sub(r"\*(.+?)\*", r"<i>\1</i>", chunk)

            result.append(chunk)

    return "".join(result)
