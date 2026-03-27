from typing import AsyncGenerator

from bot.services.llm import get_llm_client


def build_vision_messages(
    system_prompt: str,
    history: list[dict],
    b64_string: str,
    user_prompt: str,
) -> list[dict]:
    """Собираем мультимодальный messages для vision запроса."""
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_string}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": user_prompt,
                },
            ],
        }
    )
    return messages


async def stream_vision_reply(
    system_prompt: str,
    history: list[dict],
    b64_string: str,
    user_prompt: str,
    model: str,
) -> AsyncGenerator[str, None]:
    """Стримим анализ картинки от xAI Vision."""
    client = get_llm_client()
    messages = build_vision_messages(system_prompt, history, b64_string, user_prompt)

    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        timeout=60,
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content
