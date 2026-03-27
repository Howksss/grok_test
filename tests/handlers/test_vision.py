import inspect

from aiogram import Router

from bot.handlers.vision import handle_photo, router


def test_router_type():
    assert isinstance(router, Router)


def test_is_async():
    assert inspect.iscoroutinefunction(handle_photo)


def test_uses_stream_vision():
    src = inspect.getsource(handle_photo)
    assert "stream_vision_reply" in src


def test_saves_image_marker():
    """Сохраняем в историю маркер что юзер прислал картинку."""
    src = inspect.getsource(handle_photo)
    assert "[Image sent by user]" in src


def test_default_prompt():
    src = inspect.getsource(handle_photo)
    assert "Опиши что на изображении" in src


def test_checks_file_size():
    src = inspect.getsource(handle_photo)
    assert "max_image_bytes" in src or "file_size" in src


def test_uses_caption():
    src = inspect.getsource(handle_photo)
    assert "caption" in src
