import enum
import uuid
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import (
    DownloadItemStatus,
    DownloadStatus,
    PlanTier,
    StorageBackend,
    SubscriptionStatus,
    UserRole,
)


T = TypeVar("T")


class TokenType(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(BaseModel):
    user_id: uuid.UUID
    token_type: TokenType
    session_id: Optional[uuid.UUID] = None


# ---------------------------------------------------------------- Auth

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(str_strip_whitespace=True)


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: Optional[str] = None
    name: str
    avatar_url: Optional[str] = None
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    plan: Optional[PlanTier] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_.-]+$")
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# ---------------------------------------------------------------- Commands (reusable)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------- Plan / subscription

class PlanResponse(BaseModel):
    id: uuid.UUID
    tier: PlanTier
    name: str
    price_cents: int
    daily_download_limit: int
    max_file_size_mb: int
    max_concurrent_downloads: int
    max_storage_gb: int
    queue_priority: int
    features: list[Any]

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    plan: PlanResponse
    status: SubscriptionStatus
    started_at: datetime
    ends_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Downloads

class DownloadCreate(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    format: str = Field(default="mp3", pattern=r"^(mp3|m4a|opus|flac|wav)$")
    quality: Optional[str] = Field(default=None, max_length=16)

    model_config = ConfigDict(str_strip_whitespace=True)


class DownloadItemResponse(BaseModel):
    id: uuid.UUID
    url: str
    title: Optional[str] = None
    artist: Optional[str] = None
    position: int
    status: DownloadItemStatus
    file_id: Optional[uuid.UUID] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DownloadResponse(BaseModel):
    id: uuid.UUID
    url: str
    kind: str
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    cover_url: Optional[str] = None
    format: str
    quality: str
    status: DownloadStatus
    progress: int
    downloaded_bytes: int
    total_bytes: Optional[int] = None
    speed_bps: Optional[int] = None
    stage: str
    error_message: Optional[str] = None
    file_id: Optional[uuid.UUID] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    items: list[DownloadItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Library / files

class AudioMetadataResponse(BaseModel):
    id: uuid.UUID
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration_seconds: Optional[float] = None
    cover_url: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    source_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FileResponse(BaseModel):
    id: uuid.UUID
    storage: StorageBackend
    file_name: str
    mime_type: str
    format: str
    size_bytes: int
    created_at: datetime
    metadata: Optional[AudioMetadataResponse] = Field(
        default=None, validation_alias="audio_metadata", serialization_alias="metadata"
    )
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ---------------------------------------------------------------- Playlists

class PlaylistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: Optional[str] = Field(default=None, max_length=2000)
    cover_url: Optional[str] = None
    is_public: bool = False

    model_config = ConfigDict(str_strip_whitespace=True)


class PlaylistUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    description: Optional[str] = Field(default=None, max_length=2000)
    cover_url: Optional[str] = None
    is_public: Optional[bool] = None


class PlaylistItemAdd(BaseModel):
    file_id: uuid.UUID


class PlaylistItemResponse(BaseModel):
    id: uuid.UUID
    position: int
    added_at: datetime
    file: FileResponse

    model_config = ConfigDict(from_attributes=True)


class PlaylistSummary(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    is_public: bool
    track_count: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistResponse(PlaylistSummary):
    items: list[PlaylistItemResponse] = []


# ---------------------------------------------------------------- Stats

class UsageStats(BaseModel):
    daily_download_count: int
    daily_download_limit: int
    total_download_count: int
    storage_bytes: int
    storage_limit_bytes: int
    file_count: int
    playlist_count: int
    completed_downloads: int
    active_downloads: int


class UserStatsResponse(BaseModel):
    storage_bytes: int
    total_download_count: int
    completed_downloads: int
    active_downloads: int
    file_count: int
    playlist_count: int
    plan: PlanTier
    usage: UsageStats


# ---------------------------------------------------------------- Admin

class AdminUserResponse(UserResponse):
    storage_bytes: int = 0
    file_count: int = 0
    total_download_count: int = 0
    last_login_at: Optional[datetime] = None
    subscription_status: Optional[SubscriptionStatus] = None


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    plan_tier: Optional[PlanTier] = None


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_downloads: int
    active_downloads: int
    completed_downloads: int
    failed_downloads: int
    total_storage_bytes: int
    total_files: int
    total_playlists: int
    downloads_per_day: list[dict]
    status: dict


class SystemLogResponse(BaseModel):
    id: uuid.UUID
    level: str
    message: str
    source: str
    meta: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    detail: str


class MessageResponse(BaseModel):
    message: str