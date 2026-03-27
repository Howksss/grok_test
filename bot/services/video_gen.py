import httpx


async def submit_video(prompt: str, api_key: str, base_url: str) -> str:
    """Отправляем запрос на генерацию видео, возвращаем request_id для поллинга."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/videos/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": "grok-imagine-video", "prompt": prompt},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["request_id"]


async def poll_video(request_id: str, api_key: str, base_url: str) -> dict:
    """Проверяем статус генерации видео. Возвращает dict со status и video url."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{base_url}/videos/{request_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
