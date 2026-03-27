import sqlalchemy as sa

from bot.database.models import Base, Message, RateLimit, User


def test_tables_exist():
    tables = Base.metadata.tables
    assert "users" in tables
    assert "messages" in tables
    assert "rate_limits" in tables


def test_user_columns():
    cols = {c.name for c in Base.metadata.tables["users"].columns}
    assert cols >= {"id", "telegram_id", "username", "created_at", "selected_model", "cleared_at"}


def test_message_columns():
    cols = {c.name for c in Base.metadata.tables["messages"].columns}
    assert cols >= {"id", "user_id", "role", "content", "created_at"}


def test_telegram_id_bigint():
    col = Base.metadata.tables["users"].columns["telegram_id"]
    assert isinstance(col.type, sa.BigInteger)


def test_message_fk():
    col = Base.metadata.tables["messages"].columns["user_id"]
    assert len(col.foreign_keys) == 1
