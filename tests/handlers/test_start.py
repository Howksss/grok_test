import inspect

from aiogram import Router

from bot.handlers.start import cmd_start, router, _WELCOME_TEXT


def test_router_type():
    assert isinstance(router, Router)


def test_cmd_start_is_async():
    assert inspect.iscoroutinefunction(cmd_start)


def test_welcome_text_has_commands():
    for cmd in ("/model", "/new", "/reset", "/status", "/imagine pro", "/video"):
        assert cmd in _WELCOME_TEXT, f"{cmd} не найдена в приветствии"


def test_welcome_text_mentions_text_input():
    assert "напишите сообщение" in _WELCOME_TEXT
