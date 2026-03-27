from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.document | F.audio | F.sticker | F.video_note | F.voice | F.animation | F.video)
async def handle_unsupported(message: Message):
    await message.reply("Поддерживаются только текст и фотографии.")
