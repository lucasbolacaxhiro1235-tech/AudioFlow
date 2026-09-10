from datetime import timedelta
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.database import get_db
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, AuthRequest, Token,
    RefreshTokenRequest, ErrorResponse
)
from app.services.auth import (
    authenticate_user, create_user, get_user_by_id,
    create_tokens, decode_token, TokenData, TokenType
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_current_user(
    token_data: TokenData = Depends(decode_token),
    db: AsyncSession = Depends(get_db),
):
    if token_data.token_type != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return token_data.user_id


async def get_current_user_obj(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await create_user(db, user_data.email, user_data.name, user_data.password)
    return user


@router.post("/login", response_model=Token)
async def login(auth: AuthRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, auth.email, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token, refresh_token = create_tokens(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    token_data = decode_token(request.refresh_token)
    if not token_data or token_data.token_type != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    access_token, refresh_token = create_tokens(token_data.user_id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user_obj)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user


async def get_user_by_email(db: AsyncSession, email: str):
    from sqlalchemy import select
    from app.models import User
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()