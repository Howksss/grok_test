from bot.services.llm import get_llm_client


async def generate_image(prompt: str, model: str) -> str:
    """Генерация картинки через xAI images API. Возвращает url."""
    client = get_llm_client()
    response = await client.images.generate(model=model, prompt=prompt)
    return response.data[0].url
