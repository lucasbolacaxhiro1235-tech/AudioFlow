from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")
    # Core
    APP_NAME: str = "AudioFlow"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = ""
    API_BASE_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/audioflow"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    STORAGE_BACKEND: str = "local"  # local | s3 | r2
    STORAGE_LOCAL_PATH: str = "./storage"
    STORAGE_PUBLIC_BASE_URL: str = "http://localhost:8000/media"

    # S3 / R2 compatible
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "audioflow"
    S3_PUBLIC_URL: str = ""
    S3_REGION: str = "auto"

    # Email / SMTP
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@audioflow.com"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    # Audio processing
    YTDLP_PATH: str = "yt-dlp"
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"
    AUDIO_OUTPUT_FORMAT: str = "mp3"
    AUDIO_QUALITY: str = "192k"
    MAX_CONCURRENT_DOWNLOADS: int = 4
    MAX_DOWNLOAD_FILE_SIZE_MB: int = 200

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW: int = 60
    AUTH_RATE_LIMIT_REQUESTS: int = 10
    AUTH_RATE_LIMIT_WINDOW: int = 60

    # Bootstrapping
    FIRST_ADMIN_EMAIL: str = ""
    FIRST_ADMIN_PASSWORD: str = ""
    SEED_PLANS: bool = True

    # Anonymous / guest access (no login required)
    ALLOW_ANONYMOUS: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def cors_origins() -> List[str]:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    origins.extend(
        [
            settings.FRONTEND_URL,
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]
    )
    return list(dict.fromkeys(origins))