import asyncio
import base64
import time

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import openai

from bot.config import settings
from bot.database.models import User
from bot.handlers.chat import EDIT_EVERY_CHARS, MIN_EDIT_INTERVAL, _streaming_users
from bot.services.message_service import get_history, save_msg
from bot.services.moderation import check_content
from bot.services.rate_limit import check_rate_limit, record_message
from bot.services.vision import stream_vision_reply
from bot.utils.formatting import md_to_html

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message, session: AsyncSession):
    tg_id = message.from_user.id

    if tg_id in _streaming_users:
        await message.reply("Пожалуйста, дождитесь ответа.")
        return

    allowed, wait_seconds = await check_rate_limit(session, tg_id)
    if not allowed:
        await message.reply(
            f"Слишком много запросов. Подождите {wait_seconds} сек."
        )
        return

    photo = message.photo[-1]
    if photo.file_size and photo.file_size > settings.max_image_bytes:
        await message.reply(
            "Изображение слишком большое. Отправьте файл меньшего размера."
        )
        return

    _streaming_users.add(tg_id)
    accumulated = ""
    sent = None
    try:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        if user is None:
            await message.reply("Пожалуйста, отправьте /start для начала.")
            return

        prompt = message.caption or "Опиши что на изображении"

        if message.caption:
            is_safe, rejection = await check_content(message.caption)
            if not is_safe:
                await message.reply(rejection)
                return

        buf = await message.bot.download(photo)
        b64_string = base64.b64encode(buf.getvalue()).decode("utf-8")

        history = await get_history(session, user.id, settings.history_limit)

        await save_msg(session, user.id, "user", f"[Image sent by user] {prompt}")
        await record_message(session, tg_id)
        await session.commit()

        sent = await message.answer("▌")

        chars_since_edit = 0
        last_edit_time = time.monotonic()

        try:
            async for chunk in stream_vision_reply(
                system_prompt=settings.system_prompt,
                history=history,
                b64_string=b64_string,
                user_prompt=prompt,
                model=user.selected_model or settings.xai_model,
            ):
                accumulated += chunk
                chars_since_edit += len(chunk)

                if chars_since_edit >= EDIT_EVERY_CHARS:
                    now = time.monotonic()
                    elapsed = now - last_edit_time
                    if elapsed < MIN_EDIT_INTERVAL:
                        await asyncio.sleep(MIN_EDIT_INTERVAL - elapsed)
                    try:
                        await sent.edit_text(
                            md_to_html(accumulated) + " ▌",
                            parse_mode=ParseMode.HTML,
                        )
                    except Exception:
                        pass
                    chars_since_edit = 0
                    last_edit_time = time.monotonic()

            try:
                await sent.edit_text(md_to_html(accumulated.strip()), parse_mode=ParseMode.HTML)
            except Exception:
                try:
                    await sent.edit_text(accumulated.strip())
                except Exception:
                    pass

        except openai.BadRequestError:
            error_text = "Запрос отклонён модерацией. Попробуйте переформулировать."
            if sent is not None:
                try:
                    await sent.edit_text(error_text)
                except Exception:
                    await message.answer(error_text)
            else:
                await message.answer(error_text)
            return

        except Exception:
            error_text = "API недоступен, попробуйте позже."
            if sent is not None:
                try:
                    await sent.edit_text(error_text)
                except Exception:
                    await message.answer(error_text)
            else:
                await message.answer(error_text)
            return

        await save_msg(session, user.id, "assistant", accumulated.strip())
        await session.commit()

    finally:
        _streaming_users.discard(tg_id)
