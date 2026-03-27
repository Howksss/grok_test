from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.models import RateLimit


async def check_rate_limit(session: AsyncSession, telegram_id: int) -> tuple[bool, int]:
    """Проверяем рейт-лимит. Возвращаем (можно, секунд_ждать)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now - timedelta(seconds=60)

    query = select(RateLimit).where(
        RateLimit.user_id == telegram_id,
        RateLimit.window_start >= cutoff,
    )
    result = await session.execute(query)
    rows = result.scalars().all()

    total_count = sum(r.count for r in rows)

    if total_count >= settings.rate_limit_per_minute:
        oldest_window = min(r.window_start for r in rows)
        window_expires = oldest_window + timedelta(seconds=60)
        seconds_remaining = max(0, int((window_expires - now).total_seconds()))
        return (False, seconds_remaining)

    return (True, 0)


async def record_message(session: AsyncSession, telegram_id: int):
    """Записываем сообщение для рейт-лимита. Flush без commit."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    window_start = now.replace(second=0, microsecond=0)

    query = select(RateLimit).where(
        RateLimit.user_id == telegram_id,
        RateLimit.window_start == window_start,
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.count += 1
    else:
        record = RateLimit(
            user_id=telegram_id,
            window_start=window_start,
            count=1,
        )
        session.add(record)

    await session.flush()
