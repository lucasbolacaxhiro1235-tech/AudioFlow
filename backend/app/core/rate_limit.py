import time
import threading
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request, status

try:
    import redis as redis_lib

    _redis: Optional[redis_lib.Redis] = None

    def _get_redis() -> Optional[redis_lib.Redis]:
        global _redis
        if _redis is None:
            try:
                from app.config import settings

                _redis = redis_lib.Redis.from_url(
                    settings.REDIS_URL, decode_responses=True, socket_timeout=1
                )
                _redis.ping()
            except Exception:
                _redis = False  # type: ignore[assignment]
        return _redis if _redis else None
except ImportError:  # pragma: no cover
    redis_lib = None  # type: ignore[assignment]

    def _get_redis() -> Optional[object]:  # type: ignore[misc]
        return None


_memory: Dict[str, list] = {}
_lock = threading.Lock()


def _memory_check(key: str, limit: int, window: int) -> Tuple[bool, int]:
    now = time.time()
    with _lock:
        stamps = _memory.get(key, [])
        stamps = [s for s in stamps if now - s < window]
        if len(stamps) >= limit:
            _memory[key] = stamps
            return True, limit
        stamps.append(now)
        _memory[key] = stamps
        return False, len(stamps)


def _redis_check(key: str, limit: int, window: int) -> Tuple[bool, int]:
    client = _get_redis()
    if client is None:
        return _memory_check(key, limit, window)
    now = time.time()
    try:
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {now: now})
        pipe.expire(key, window)
        _, count, _, _ = pipe.execute()
        return count >= limit, count
    except Exception:
        return _memory_check(key, limit, window)


async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    client_ip = _client_ip(request)
    key = f"ratelimit:{client_ip}:{request.url.path}"
    limited, _ = _redis_check(key, limit, window)
    if limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(window)},
        )


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"