import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_user_plan
from app.core.rate_limit import rate_limit
from app.database import get_db
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LogoutRequest,
    MessageResponse,
    PlanTier,
    RefreshTokenRequest,
    ResetPasswordRequest,
    ResendVerificationRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    VerifyEmailRequest,
)
from app.services import auth as auth_service
from app.services.email import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user: User, plan_tier: PlanTier = PlanTier.FREE) -> UserResponse:
    data = UserResponse.model_validate(user)
    data.plan = plan_tier
    return data


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await rate_limit(request, limit=20, window=3600)
    if await auth_service.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if payload.username and await auth_service.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already taken")

    user = await auth_service.create_user(
        db,
        email=str(payload.email),
        name=payload.name,
        password=payload.password,
        username=payload.username,
    )
    token = await auth_service.create_email_verification(db, user)
    send_verification_email(user.email, token)
    return _user_response(user)


@router.post("/login", response_model=Token)
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    from app.schemas import AuthRequest

    await rate_limit(request, limit=10, window=60)
    body = await request.json()
    try:
        payload = AuthRequest(**body)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid input")

    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
    access_token, refresh_token = await auth_service.create_session(
        db, user, ip_address=ip, user_agent=request.headers.get("user-agent")
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    session = await auth_service.is_session_valid(db, payload.refresh_token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    from app.core.security import create_access_token, create_refresh_token, hash_token

    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_refresh = create_refresh_token(session.user_id, session.id)
    session.refresh_token_hash = hash_token(new_refresh)
    session.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    await db.commit()

    return Token(access_token=create_access_token(session.user_id), refresh_token=new_refresh)


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    if payload.refresh_token:
        await auth_service.revoke_session(db, payload.refresh_token)
    return MessageResponse(message="Logged out")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.verify_email_token(db, payload.token)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return MessageResponse(message="Email verified")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(payload: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(db, str(payload.email))
    if user is None:
        return MessageResponse(message="If the email exists, a new verification was sent")
    if user.email_verified:
        return MessageResponse(message="Email already verified")
    token = await auth_service.create_email_verification(db, user)
    send_verification_email(user.email, token)
    return MessageResponse(message="Verification email sent")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(db, str(payload.email))
    if user is not None:
        token = await auth_service.create_password_reset(db, user)
        send_password_reset_email(user.email, token)
    return MessageResponse(message="If the email exists, a reset link was sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.reset_password(db, payload.token, payload.new_password)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import hash_password, verify_password

    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return MessageResponse(message="Password changed")