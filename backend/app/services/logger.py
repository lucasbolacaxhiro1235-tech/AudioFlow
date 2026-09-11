import logging
from typing import Optional

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import LogLevel, SystemLog

logger = logging.getLogger(__name__)


async def write_log(
    level: LogLevel = LogLevel.INFO,
    message: str = "",
    source: str = "app",
    meta: Optional[dict] = None,
) -> None:
    if not settings.DEBUG and level in (LogLevel.DEBUG, LogLevel.INFO) and source == "app":
        pass
    try:
        async with AsyncSessionLocal() as db:
            db.add(SystemLog(level=level, message=message, source=source, meta=meta))
            await db.commit()
    except Exception as exc:
        logger.warning("Failed to write system log: %s", exc)