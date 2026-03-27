import asyncio
import logging
import time

import httpx
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.engine import async_session
from bot.database.models import User
from bot.services.message_service import save_msg
from bot.services.moderation import check_content
from bot.services.rate_limit import check_rate_limit, record_message
from bot.services.video_gen import poll_video, submit_video

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("video"))
async def handle_video(message: Message, session: AsyncSession):
    tg_id = message.from_user.id

    parts = message.text.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""

    if not args.strip():
        await message.reply(
            "Укажите описание после команды. Пример: /video a cat playing piano"
        )
        return

    is_safe, rejection = await check_content(args.strip())
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
    await save_msg(session, user.id, "user", f"[/video: {args.strip()}]")
    await session.commit()

    await message.react([ReactionTypeEmoji(emoji="👀")])
    status_msg = await message.answer("Генерирую видео...")

    try:
        request_id = await submit_video(
            args.strip(), settings.xai_api_key, settings.xai_base_url
        )
    except httpx.HTTPError as exc:
        logger.error("Video submit failed: %s", exc)
        await status_msg.edit_text("API недоступен, попробуйте позже")
        return

    task = asyncio.create_task(
        _video_poll_task(
            message.bot,
            message.chat.id,
            status_msg.message_id,
            request_id,
            user.id,
            message.message_id,
        )
    )
    task.add_done_callback(
        lambda t: t.result() if not t.cancelled() and not t.exception() else None
    )


async def _video_poll_task(
    bot: Bot,
    chat_id: int,
    status_msg_id: int,
    request_id: str,
    user_id: int,
    original_msg_id: int,
):
    """Фоновая задача: поллим xAI пока видео не сгенерится или не упадёт таймаут."""
    start = time.monotonic()
    poll_interval = settings.video_poll_interval
    timeout = settings.video_timeout

    try:
        while True:
            elapsed = int(time.monotonic() - start)

            if elapsed >= timeout:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    text="Генерация видео заняла слишком долго. Попробуйте позже.",
                )
                return

            await asyncio.sleep(poll_interval)

            result = await poll_video(
                request_id, settings.xai_api_key, settings.xai_base_url
            )
            status = result.get("status")

            if status == "done":
                video_url = result.get("video", {}).get("url")
                if video_url:
                    await bot.send_video(chat_id=chat_id, video=video_url)
                await bot.delete_message(chat_id=chat_id, message_id=status_msg_id)
                try:
                    await bot.set_message_reaction(
                        chat_id=chat_id,
                        message_id=original_msg_id,
                        reaction=[ReactionTypeEmoji(emoji="👍")],
                    )
                except Exception:
                    pass

                async with async_session() as bg_session:
                    await save_msg(bg_session, user_id, "assistant", "[Видео сгенерировано]")
                    await bg_session.commit()
                return

            if status in ("failed", "expired"):
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    text="Не удалось сгенерировать видео. Попробуйте позже.",
                )
                return

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"Генерирую видео... ({elapsed}с)",
            )

    except Exception as exc:
        logger.error("Unexpected error in video poll task: %s", exc, exc_info=True)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text="Произошла ошибка при генерации видео. Попробуйте позже.",
            )
        except Exception:
            pass
