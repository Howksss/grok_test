from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import BaseMiddleware

from bot.database.middleware import DbSessionMiddleware


def test_inherits_base_middleware():
    assert issubclass(DbSessionMiddleware, BaseMiddleware)


def test_stores_session_pool():
    pool = MagicMock()
    mw = DbSessionMiddleware(session_pool=pool)
    assert mw.session_pool is pool
