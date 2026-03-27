import inspect

from aiogram import Router

from bot.handlers.video import handle_video, _video_poll_task, router


def test_router_type():
    assert isinstance(router, Router)


def test_is_async():
    assert inspect.iscoroutinefunction(handle_video)
    assert inspect.iscoroutinefunction(_video_poll_task)


def test_submits_video():
    src = inspect.getsource(handle_video)
    assert "submit_video" in src


def test_background_polling():
    """Поллинг должен быть fire-and-forget через create_task."""
    src = inspect.getsource(handle_video)
    assert "create_task" in src
    assert "add_done_callback" in src


def test_validates_empty_prompt():
    src = inspect.getsource(handle_video)
    assert "Укажите описание" in src


def test_poll_has_timeout():
    src = inspect.getsource(_video_poll_task)
    assert "timeout" in src or "video_timeout" in src


def test_poll_sends_video():
    src = inspect.getsource(_video_poll_task)
    assert "send_video" in src


def test_poll_shows_elapsed():
    src = inspect.getsource(_video_poll_task)
    assert "elapsed" in src


def test_poll_no_session_param():
    """Фоновая таска открывает свою сессию, а не принимает извне."""
    sig = inspect.signature(_video_poll_task)
    assert "session" not in sig.parameters
