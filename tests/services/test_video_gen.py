import inspect

from bot.services.video_gen import submit_video, poll_video


def test_submit_is_async():
    assert inspect.iscoroutinefunction(submit_video)


def test_poll_is_async():
    assert inspect.iscoroutinefunction(poll_video)


def test_submit_uses_httpx():
    src = inspect.getsource(submit_video)
    assert "httpx" in src


def test_submit_endpoint():
    src = inspect.getsource(submit_video)
    assert "videos/generations" in src


def test_poll_endpoint():
    src = inspect.getsource(poll_video)
    assert "videos/" in src


def test_submit_returns_request_id():
    src = inspect.getsource(submit_video)
    assert "request_id" in src
