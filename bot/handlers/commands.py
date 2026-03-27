from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.keyboards.models import MODEL_CB_PREFIX, build_model_keyboard
from bot.database.models import User
from bot.services.message_service import count_session_messages

router = Router()


@router.message(Command("model"))
async def cmd_model(message: Message):
    await message.answer("Выберите модель:", reply_markup=build_model_keyboard())


@router.callback_query(F.data.startswith(MODEL_CB_PREFIX))
async def callback_model_select(callback: CallbackQuery, session: AsyncSession):
    model_name = callback.data[len(MODEL_CB_PREFIX):]

    user = await session.scalar(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    if user is not None:
        user.selected_model = model_name
        await session.commit()

    await callback.answer()
    await callback.message.edit_text(f"Модель изменена на {model_name}")


@router.message(Command("new"))
@router.message(Command("reset"))
async def cmd_reset(message: Message, session: AsyncSession):
    """Мягкий сброс: ставим cleared_at, старые сообщения остаются в бд."""
    user = await session.scalar(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    if user is not None:
        user.cleared_at = datetime.utcnow()
        await session.commit()

    await message.answer("Сессия сброшена. Начните новый диалог.")


@router.message(Command("status"))
async def cmd_status(message: Message, session: AsyncSession):
    user = await session.scalar(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    if user is None:
        await message.answer("Пожалуйста, отправьте /start для начала.")
        return

    model_name = user.selected_model or settings.xai_model
    count = await count_session_messages(session, user.id)

    await message.answer(
        f"Статус\n"
        f"Модель: {model_name}\n"
        f"Сообщений в сессии: {count}"
    )
