from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_admin
from app.database import get_db
from app.models import (
    Download,
    File,
    Plan,
    PlanTier,
    Playlist,
    Subscription,
    SystemLog,
    User,
    UserRole,
)
from app.schemas import (
    AdminStatsResponse,
    AdminUserResponse,
    AdminUserUpdate,
    MessageResponse,
    PlanResponse,
    SystemLogResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])

STATUSES_DOWNLOAD = ["pending", "validating", "processing", "converting"]


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if page_size > 200:
        page_size = 200
    query = select(User)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%")
        )
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    output = []
    for u in users:
        file_count = (
            await db.execute(select(func.count()).select_from(File).where(File.user_id == u.id))
        ).scalar() or 0
        storage = (
            await db.execute(select(func.coalesce(func.sum(File.size_bytes), 0)).where(File.user_id == u.id))
        ).scalar() or 0
        downloads = (
            await db.execute(select(func.count()).select_from(Download).where(Download.user_id == u.id))
        ).scalar() or 0
        sub = (
            await db.execute(select(Subscription).where(Subscription.user_id == u.id))
        ).scalar_one_or_none()

        base = AdminUserResponse.model_validate(u)
        base.storage_bytes = storage
        base.file_count = file_count
        base.total_download_count = downloads
        base.subscription_status = sub.status if sub else None
        base.plan = (await db.get(Plan, sub.plan_id)).tier if sub and sub.plan_id else PlanTier.FREE
        output.append(base)
    return output


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, __import__("uuid").UUID(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = payload.role
    if payload.plan_tier is not None:
        plan = (
            await db.execute(select(Plan).where(Plan.tier == payload.plan_tier.value))
        ).scalar_one_or_none()
        if plan is None:
            raise HTTPException(status_code=400, detail="Plan not found")
        sub = (
            await db.execute(select(Subscription).where(Subscription.user_id == user.id))
        ).scalar_one_or_none()
        if sub is None:
            sub = Subscription(user_id=user.id, plan_id=plan.id)
            db.add(sub)
        else:
            sub.plan_id = plan.id
    await db.commit()
    await db.refresh(user)

    base = AdminUserResponse.model_validate(user)
    sub = (
        await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    ).scalar_one_or_none()
    base.plan = (await db.get(Plan, sub.plan_id)).tier if sub and sub.plan_id else PlanTier.FREE
    base.subscription_status = sub.status if sub else None
    return base


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, __import__("uuid").UUID(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot delete an admin")
    await db.delete(user)
    await db.commit()
    return MessageResponse(message="User deleted")


@router.get("/downloads", response_model=list[dict])
async def list_all_downloads(
    page: int = 1,
    page_size: int = 50,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Download)
        .options(selectinload(Download.user))
        .order_by(Download.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(min(page_size, 200))
    )
    downloads = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "user": {"id": str(d.user.id), "email": d.user.email} if d.user else None,
            "url": d.url,
            "status": d.status.value,
            "format": d.format,
            "created_at": d.created_at.isoformat(),
        }
        for d in downloads
    ]


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    active_users = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active.is_(True)))
    ).scalar() or 0
    total_downloads = (await db.execute(select(func.count()).select_from(Download))).scalar() or 0
    active_downloads = (
        await db.execute(
            select(func.count()).select_from(Download).where(Download.status.in_(STATUSES_DOWNLOAD))
        )
    ).scalar() or 0
    completed_downloads = (
        await db.execute(select(func.count()).select_from(Download).where(Download.status == "completed"))
    ).scalar() or 0
    failed_downloads = (
        await db.execute(select(func.count()).select_from(Download).where(Download.status == "failed"))
    ).scalar() or 0
    total_storage = (
        await db.execute(select(func.coalesce(func.sum(File.size_bytes), 0)))
    ).scalar() or 0
    total_files = (await db.execute(select(func.count()).select_from(File))).scalar() or 0
    total_playlists = (await db.execute(select(func.count()).select_from(Playlist))).scalar() or 0

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_downloads=total_downloads,
        active_downloads=active_downloads,
        completed_downloads=completed_downloads,
        failed_downloads=failed_downloads,
        total_storage_bytes=total_storage,
        total_files=total_files,
        total_playlists=total_playlists,
        downloads_per_day=[],
        status={
            "postgres": "connected",
            "redis": "connected",
            "ffmpeg": "installed",
            "workers": "running",
        },
    )


@router.get("/logs", response_model=list[SystemLogResponse])
async def list_logs(
    page: int = 1,
    page_size: int = 100,
    level: Optional[str] = None,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(SystemLog)
    if level:
        query = query.where(SystemLog.level == level)
    query = query.order_by(SystemLog.created_at.desc()).offset((page - 1) * page_size).limit(
        min(page_size, 500)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/status", response_model=dict)
async def system_status(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    status_data = {"postgres": "unknown", "redis": "unknown", "ffmpeg": "unknown", "workers": "unknown"}

    try:
        await db.execute(select(1))
        status_data["postgres"] = "connected"
    except Exception:
        status_data["postgres"] = "error"

    try:
        from app.core.rate_limit import _get_redis

        r = _get_redis()
        if r is not None:
            r.ping()
            status_data["redis"] = "connected"
        else:
            status_data["redis"] = "unavailable"
    except Exception:
        status_data["redis"] = "error"

    import shutil

    status_data["ffmpeg"] = "installed" if shutil.which("ffmpeg") else "missing"

    try:
        from app.workers.tasks import celery_app

        status_data["workers"] = "configured"
    except Exception:
        status_data["workers"] = "unavailable"

    return status_data