from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User

router = Router()

_WELCOME_TEXT = (
    "Привет! Я — ассистент на базе Grok.\n\n"
    "<b>Диалог</b>\n"
    "/new — новый диалог\n"
    "/reset — сбросить контекст\n\n"
    "<b>Настройки</b>\n"
    "/model — выбрать модель\n"
    "/status — текущий статус\n\n"
    "<b>Генерация</b>\n"
    "/imagine prompt — генерация изображения\n"
    "/imagine pro prompt — pro-качество\n"
    "/video prompt — генерация видео\n\n"
    "Или просто напишите сообщение."
)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    tg_id = message.from_user.id
    username = message.from_user.username

    user = await session.scalar(select(User).where(User.telegram_id == tg_id))
    if user is None:
        user = User(telegram_id=tg_id, username=username)
        session.add(user)
    elif user.username != username:
        user.username = username

    await session.commit()
    await message.answer(_WELCOME_TEXT, parse_mode=ParseMode.HTML)
