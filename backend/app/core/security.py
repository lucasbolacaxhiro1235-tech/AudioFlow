import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jose import JWTError, jwt

from app.config import settings
from app.schemas import TokenData, TokenType

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError, ValueError):
        return False


def _create_token(data: dict, expires_delta: timedelta, token_type: TokenType) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update(
        {
            "exp": now + expires_delta,
            "iat": now,
            "type": token_type.value,
        }
    )
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: uuid.UUID) -> str:
    return _create_token(
        {"sub": str(user_id)},
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        TokenType.ACCESS,
    )


def create_refresh_token(user_id: uuid.UUID, session_id: uuid.UUID) -> str:
    return _create_token(
        {"sub": str(user_id), "sid": str(session_id)},
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        TokenType.REFRESH,
    )


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type is None:
            return None
        return TokenData(
            user_id=uuid.UUID(user_id),
            token_type=TokenType(token_type),
            session_id=uuid.UUID(payload["sid"]) if payload.get("sid") else None,
        )
    except (JWTError, ValueError, KeyError):
        return None


def generate_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_secret_key() -> str:
    return secrets.token_urlsafe(32)