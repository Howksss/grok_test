import inspect

from aiogram import Router

from bot.handlers.unsupported import handle_unsupported, router


def test_router_type():
    assert isinstance(router, Router)


def test_is_async():
    assert inspect.iscoroutinefunction(handle_unsupported)


def test_mentions_supported_types():
    src = inspect.getsource(handle_unsupported)
    assert "текст" in src
    assert "фотографии" in src


def test_covers_media_types():
    """Фильтр должен ловить основные типы медиа."""
    src = inspect.getsource(handle_unsupported)
    for media in ("document", "audio", "sticker", "voice", "video"):
        assert media in src, f"не покрыт тип {media}"
