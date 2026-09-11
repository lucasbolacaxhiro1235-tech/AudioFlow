import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_user_plan
from app.database import get_db
from app.models import Download, File, Playlist, PlanTier, Subscription, User
from app.schemas import UserResponse, UserStatsResponse, UserUpdate, UsageStats
from app.services.usage import get_usage

me_router = APIRouter(prefix="/me", tags=["me"])
user_router = APIRouter(prefix="/user", tags=["user"])


def _to_plan(user: User, plan) -> UserResponse:
    data = UserResponse.model_validate(user)
    data.plan = plan.tier if plan else PlanTier.FREE
    return data


@me_router.get("", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await get_user_plan(db, user.id)
    return _to_plan(user, plan)


@me_router.patch("", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.name is not None:
        user.name = payload.name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    if payload.username is not None:
        existing = await db.execute(select(User).where(User.username == payload.username, User.id != user.id))
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=409, detail="Username already taken")
        user.username = payload.username
    await db.commit()
    await db.refresh(user)
    plan = await get_user_plan(db, user.id)
    return _to_plan(user, plan)


@user_router.get("/stats", response_model=UserStatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await get_user_plan(db, user.id)
    usage = await get_usage(db, user.id)

    file_count = (
        await db.execute(
            select(func.count()).select_from(File).where(File.user_id == user.id, File.deleted_at.is_(None))
        )
    ).scalar() or 0
    playlist_count = (
        await db.execute(
            select(func.count()).select_from(Playlist).where(Playlist.user_id == user.id)
        )
    ).scalar() or 0
    completed = (
        await db.execute(
            select(func.count())
            .select_from(Download)
            .where(Download.user_id == user.id, Download.status == "completed")
        )
    ).scalar() or 0
    active = (
        await db.execute(
            select(func.count())
            .select_from(Download)
            .where(
                Download.user_id == user.id,
                Download.status.in_(["pending", "validating", "processing", "converting"]),
            )
        )
    ).scalar() or 0

    storage_limit = plan.max_storage_gb * 1024 * 1024 * 1024
    usage_stats = UsageStats(
        daily_download_count=usage.daily_download_count,
        daily_download_limit=plan.daily_download_limit,
        total_download_count=usage.total_download_count,
        storage_bytes=usage.storage_bytes,
        storage_limit_bytes=storage_limit,
        file_count=file_count,
        playlist_count=playlist_count,
        completed_downloads=completed,
        active_downloads=active,
    )
    return UserStatsResponse(
        storage_bytes=usage.storage_bytes,
        total_download_count=usage.total_download_count,
        completed_downloads=completed,
        active_downloads=active,
        file_count=file_count,
        playlist_count=playlist_count,
        plan=plan.tier,
        usage=usage_stats,
    )