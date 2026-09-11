import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.security import decode_token, hash_password
from app.database import get_db
from app.models import Plan, PlanTier, Subscription, User, UserRole
from app.schemas import TokenType

_bearer = HTTPBearer(auto_error=False)


async def _get_guest_user(db: AsyncSession, client_id: str) -> User:
    username = f"guest_{client_id.replace('-', '')}"
    result = await db.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    user = User(
        email=f"guest+{client_id}@audioflow.pages.dev",
        name="Visitante",
        username=username,
        hashed_password=hash_password(uuid.uuid4().hex),
        role=UserRole.USER,
        email_verified=False,
    )
    db.add(user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        result = await db.execute(select(User).where(User.username == username))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing
        raise
    await db.refresh(user)
    return user


def _client_id(request: Request) -> Optional[str]:
    raw = request.headers.get("x-client-id") or request.headers.get("X-Client-Id")
    if not raw:
        return None
    try:
        return str(uuid.UUID(raw.strip()[:36])) if len(raw.strip()) >= 32 else None
    except ValueError:
        return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is not None:
        token_data = decode_token(credentials.credentials)
        if token_data is not None and token_data.token_type == TokenType.ACCESS:
            user = await db.get(User, token_data.user_id)
            if user is not None and user.is_active:
                return user

    if settings.ALLOW_ANONYMOUS:
        client_id = _client_id(request)
        if client_id is not None:
            return await _get_guest_user(db, client_id)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


async def get_user_plan(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Plan:
    result = await db.execute(
        select(Plan)
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.user_id == user_id)
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if plan is not None:
        return plan
    result = await db.execute(select(Plan).where(Plan.tier == PlanTier.FREE).limit(1))
    plan = result.scalar_one_or_none()
    if plan is None:
        return Plan(
            tier=PlanTier.FREE,
            name="Free",
            daily_download_limit=10,
            max_file_size_mb=50,
            max_concurrent_downloads=1,
            max_storage_gb=1,
            queue_priority=0,
            features=[],
        )
    return plan