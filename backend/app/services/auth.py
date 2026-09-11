import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models import (
    EmailVerification,
    PasswordReset,
    Session,
    User,
    UserRole,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession,
    email: str,
    name: str,
    password: str,
    username: Optional[str] = None,
    role: UserRole = UserRole.USER,
) -> User:
    user = User(
        email=email.lower(),
        name=name.strip(),
        username=username.strip() if username else None,
        hashed_password=hash_password(password),
        role=role,
        email_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_session(
    db: AsyncSession,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> tuple[str, str]:
    session = Session(
        user_id=user.id,
        refresh_token_hash="pending",
        expires_at=_utcnow() + timedelta(days=30),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    refresh_token = create_refresh_token(user.id, session.id)
    session.refresh_token_hash = hash_token(refresh_token)
    await db.commit()

    access_token = create_access_token(user.id)
    return access_token, refresh_token


async def revoke_session(db: AsyncSession, refresh_token: str) -> bool:
    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(Session).where(Session.refresh_token_hash == token_hash)
    )
    session = result.scalar_one_or_none()
    if session is None:
        return False
    session.revoked_at = _utcnow()
    await db.commit()
    return True


async def is_session_valid(db: AsyncSession, refresh_token: str) -> Optional[Session]:
    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(Session).where(Session.refresh_token_hash == token_hash)
    )
    session = result.scalar_one_or_none()
    if session is None or session.revoked_at is not None:
        return None
    if session.expires_at < _utcnow():
        return None
    return session


async def create_email_verification(db: AsyncSession, user: User) -> str:
    token = generate_token()
    existing = await db.execute(
        select(EmailVerification).where(EmailVerification.user_id == user.id)
    )
    for item in existing.scalars().all():
        await db.delete(item)
    record = EmailVerification(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=_utcnow() + timedelta(hours=24),
    )
    db.add(record)
    await db.commit()
    return token


async def verify_email_token(db: AsyncSession, token: str) -> Optional[User]:
    token_hash = hash_token(token)
    result = await db.execute(
        select(EmailVerification).where(EmailVerification.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    if record.verified_at is not None:
        return None
    if record.expires_at < _utcnow():
        return None
    record.verified_at = _utcnow()
    user = await db.get(User, record.user_id)
    if user is not None:
        user.email_verified = True
    await db.commit()
    return user


async def create_password_reset(db: AsyncSession, user: User) -> str:
    token = generate_token()
    existing = await db.execute(
        select(PasswordReset).where(
            PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None)
        )
    )
    for item in existing.scalars().all():
        item.used_at = _utcnow()
    record = PasswordReset(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=_utcnow() + timedelta(hours=1),
    )
    db.add(record)
    await db.commit()
    return token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> Optional[User]:
    token_hash = hash_token(token)
    result = await db.execute(
        select(PasswordReset).where(
            PasswordReset.token_hash == token_hash, PasswordReset.used_at.is_(None)
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    if record.expires_at < _utcnow():
        return None
    user = await db.get(User, record.user_id)
    if user is None:
        return None
    user.hashed_password = hash_password(new_password)
    record.used_at = _utcnow()
    await db.commit()
    return user