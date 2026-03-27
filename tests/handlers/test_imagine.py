import inspect

from aiogram import Router

from bot.handlers.imagine import handle_imagine, router


def test_router_type():
    assert isinstance(router, Router)


def test_is_async():
    assert inspect.iscoroutinefunction(handle_imagine)


def test_supports_pro_model():
    """В хэндлере должна быть логика выбора pro-модели."""
    src = inspect.getsource(handle_imagine)
    assert "grok-imagine-image-pro" in src
    assert "grok-imagine-image" in src


def test_validates_empty_prompt():
    src = inspect.getsource(handle_imagine)
    assert "Укажите описание" in src


def test_handles_api_errors():
    src = inspect.getsource(handle_imagine)
    assert "RateLimitError" in src
    assert "BadRequestError" in src
    assert "APIError" in src


def test_sends_photo():
    src = inspect.getsource(handle_imagine)
    assert "answer_photo" in src


def test_saves_history():
    src = inspect.getsource(handle_imagine)
    assert "save_msg" in src
