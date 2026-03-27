from typing import AsyncGenerator

from openai import AsyncOpenAI

from bot.config import settings

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    """Синглтон клиент для xAI API."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.xai_api_key,
            base_url=settings.xai_base_url,
        )
    return _client


async def stream_reply(
    system_prompt: str,
    history: list[dict],
    user_message: str,
    model: str,
) -> AsyncGenerator[str, None]:
    """Стримим ответ от xAI, yield'им текстовые чанки."""
    client = get_llm_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

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
