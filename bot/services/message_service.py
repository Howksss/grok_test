from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Message, User


async def get_history(session: AsyncSession, user_id: int, limit: int) -> list[dict]:
    """Загружаем историю сообщений с учётом cleared_at."""
    user = await session.get(User, user_id)

    query = (
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    if user is not None and user.cleared_at is not None:
        query = query.where(Message.created_at > user.cleared_at)

    result = await session.execute(query)
    rows = result.scalars().all()

    return [{"role": m.role, "content": m.content} for m in reversed(rows)]


async def save_msg(session: AsyncSession, user_id: int, role: str, content: str) -> Message:
    """Сохраняем сообщение. Flush без commit - коммитит вызывающий код."""
    msg = Message(user_id=user_id, role=role, content=content)
    session.add(msg)
    await session.flush()
    return msg


async def count_session_messages(session: AsyncSession, user_id: int) -> int:
    """Считаем кол-во сообщений в текущей сессии (с учётом cleared_at)."""
    user = await session.get(User, user_id)

    query = select(func.count()).select_from(Message).where(Message.user_id == user_id)

    if user is not None and user.cleared_at is not None:
        query = query.where(Message.created_at > user.cleared_at)

    result = await session.execute(query)
    return result.scalar_one()
