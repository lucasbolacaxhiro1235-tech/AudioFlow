import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Download, File, Plan, Usage


def _day_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def get_usage(db: AsyncSession, user_id: uuid.UUID) -> Usage:
    result = await db.execute(select(Usage).where(Usage.user_id == user_id))
    usage = result.scalar_one_or_none()
    if usage is None:
        usage = Usage(user_id=user_id, day_key=_day_key())
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
    elif usage.day_key != _day_key():
        usage.day_key = _day_key()
        usage.daily_download_count = 0
        await db.commit()
    return usage


async def increment_download_count(db: AsyncSession, user_id: uuid.UUID) -> Usage:
    usage = await get_usage(db, user_id)
    usage.daily_download_count += 1
    usage.total_download_count += 1
    await db.commit()
    return usage


async def add_storage_bytes(db: AsyncSession, user_id: uuid.UUID, size_bytes: int) -> Usage:
    usage = await get_usage(db, user_id)
    usage.storage_bytes += size_bytes
    await db.commit()
    return usage


async def remove_storage_bytes(db: AsyncSession, user_id: uuid.UUID, size_bytes: int) -> Usage:
    usage = await get_usage(db, user_id)
    usage.storage_bytes = max(0, usage.storage_bytes - size_bytes)
    await db.commit()
    return usage


async def get_user_storage_used(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(File.size_bytes).where(File.user_id == user_id, File.deleted_at.is_(None))
    )
    return sum(size for (size,) in result.all())


async def count_active_downloads(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(Download.id).where(
            Download.user_id == user_id,
            Download.status.in_(["pending", "validating", "processing", "converting"]),
        )
    )
    return len(result.scalars().all())


async def can_initiate_download(
    db: AsyncSession,
    user_id: uuid.UUID,
    plan: Plan,
) -> tuple[bool, str]:
    usage = await get_usage(db, user_id)
    if usage.daily_download_count >= plan.daily_download_limit:
        return False, "Limite diário de downloads atingido"
    active = await count_active_downloads(db, user_id)
    if active >= plan.max_concurrent_downloads:
        return False, "Limite de downloads simultâneos atingido"
    return True, ""