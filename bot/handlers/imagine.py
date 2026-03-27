import logging

import openai
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji, URLInputFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.services.image_gen import generate_image
from bot.services.message_service import save_msg
from bot.services.moderation import check_content
from bot.services.rate_limit import check_rate_limit, record_message

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("imagine"))
async def handle_imagine(message: Message, session: AsyncSession):
    tg_id = message.from_user.id

    parts = message.text.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""

    args_lower = args.lower()
    if args_lower.startswith("pro "):
        model = "grok-imagine-image-pro"
        prompt = args[4:].strip()
    elif args_lower == "pro":
        model = "grok-imagine-image-pro"
        prompt = ""
    else:
        model = "grok-imagine-image"
        prompt = args.strip()

    if not prompt:
        await message.reply(
            "Укажите описание после команды. Пример: /imagine sunset over mountains"
        )
        return

    is_safe, rejection = await check_content(prompt)
    if not is_safe:
        await message.reply(rejection)
        return

    allowed, wait_seconds = await check_rate_limit(session, tg_id)
    if not allowed:
        await message.reply(
            f"Слишком много запросов. Подождите {wait_seconds} сек."
        )
        return

    user = await session.scalar(select(User).where(User.telegram_id == tg_id))
    if user is None:
        await message.reply("Пожалуйста, отправьте /start для начала.")
        return

    await record_message(session, tg_id)
    await session.commit()

    await message.react([ReactionTypeEmoji(emoji="👀")])
    placeholder = await message.answer("Генерирую изображение...")

    try:
        url = await generate_image(prompt, model)
        await message.answer_photo(URLInputFile(url))
        await placeholder.delete()
        await message.react([ReactionTypeEmoji(emoji="👍")])

        await save_msg(session, user.id, "user", f"[/imagine: {prompt}]")
        await save_msg(session, user.id, "assistant", "[Изображение сгенерировано]")
        await session.commit()

    except openai.RateLimitError:
        await placeholder.edit_text("Слишком много запросов. Подождите немного.")

    except openai.BadRequestError:
        await placeholder.edit_text(
            "Запрос отклонён модерацией. Попробуйте изменить промпт."
        )

    except openai.APIError:
        await placeholder.edit_text("API недоступен, попробуйте позже")

    except Exception as exc:
        logger.error("Unexpected error in handle_imagine: %s", exc, exc_info=True)
        await placeholder.edit_text("API недоступен, попробуйте позже")
