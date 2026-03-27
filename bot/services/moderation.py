import logging

from bot.config import settings
from bot.services.llm import get_llm_client

logger = logging.getLogger(__name__)

_MODERATION_SYSTEM_PROMPT = (
    "Ты — фильтр контент-модерации. Твоя задача — определить, содержит ли "
    "запрос пользователя запрещённые темы. Запрещённые темы:\n"
    "- Детская порнография или сексуальная эксплуатация несовершеннолетних\n"
    "- Терроризм: создание оружия, взрывчатых веществ, организация терактов\n"
    "- ЛГБТ-пропаганда\n"
    "- Наркотики: изготовление, продажа\n"
    "- Экстремизм, разжигание ненависти\n"
    "- Инструкции по причинению вреда людям\n\n"
    "Отвечай СТРОГО одним словом:\n"
    "OK — если запрос безопасен\n"
    "BLOCKED — если запрос содержит запрещённые темы\n\n"
    "Ничего кроме одного слова не пиши."
)


async def check_content(user_text: str) -> tuple[bool, str | None]:
    client = get_llm_client()

    try:
        response = await client.chat.completions.create(
            model=settings.moderation_model,
            messages=[
                {"role": "system", "content": _MODERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            stream=False,
            timeout=15,
        )

        verdict = response.choices[0].message.content.strip().upper()

        if verdict == "BLOCKED":
            return False, "Запрос содержит запрещённую тему и не может быть обработан."

        return True, None

    except Exception as exc:
        logger.warning("Moderation check failed, allowing request: %s", exc)
        return True, None
