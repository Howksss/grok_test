import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import settings
from bot.database.engine import async_session, engine
from bot.database.middleware import DbSessionMiddleware
from bot.handlers.start import router as start_router
from bot.handlers.commands import router as commands_router
from bot.handlers.vision import router as vision_router
from bot.handlers.imagine import router as imagine_router
from bot.handlers.video import router as video_router
from bot.handlers.unsupported import router as unsupported_router
from bot.handlers.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="model", description="Выбрать модель"),
        BotCommand(command="new", description="Новый диалог"),
        BotCommand(command="reset", description="Сбросить контекст"),
        BotCommand(command="status", description="Текущий статус"),
        BotCommand(command="imagine", description="Изображение (/imagine pro для pro-качества)"),
        BotCommand(command="video", description="Сгенерировать видео"),
    ])
    logging.info("Bot started")


async def on_shutdown(bot: Bot):
    await engine.dispose()
    logging.info("Bot stopped, engine disposed")


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))

    dp.include_router(start_router)
    dp.include_router(commands_router)
    dp.include_router(imagine_router)
    dp.include_router(video_router)
    dp.include_router(vision_router)
    dp.include_router(unsupported_router)
    dp.include_router(chat_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
