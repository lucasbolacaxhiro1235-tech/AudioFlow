from celery import Celery
from app.config import settings

celery_app = Celery(
    "audioflow",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=86400,
    task_routes={
        "app.workers.tasks.process_download": {"queue": "downloads"},
        "app.workers.tasks.process_playlist": {"queue": "downloads"},
    },
    beat_schedule={},
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_download_task(self, download_id: str):
    import asyncio
    from uuid import UUID
    from app.workers.audio_processor import audio_processor

    try:
        result = asyncio.run(audio_processor.process_download(UUID(download_id)))
        return {"success": result, "download_id": download_id}
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def process_playlist_task(self, playlist_url: str, user_id: str):
    import asyncio
    from uuid import UUID
    import yt_dlp
    from app.database import AsyncSessionLocal
    from app.models import Download, DownloadStatus, User
    from sqlalchemy import select

    async def _process():
        ydl_opts = {
            "extract_flat": True,
            "quiet": True,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(playlist_url, download=False)
                if not info or "entries" not in info:
                    return {"success": False, "error": "Invalid playlist"}

                track_urls = []
                for entry in info["entries"]:
                    if entry and entry.get("url"):
                        track_urls.append(entry["url"])

                async with AsyncSessionLocal() as db:
                    user = await db.get(User, UUID(user_id))
                    if not user:
                        return {"success": False, "error": "User not found"}

                    downloads = []
                    for track_url in track_urls:
                        download = Download(
                            user_id=user.id,
                            spotify_url=track_url,
                            status=DownloadStatus.PENDING,
                        )
                        db.add(download)
                        downloads.append(download)

                    await db.commit()

                    for download in downloads:
                        await db.refresh(download)
                        process_download_task.delay(str(download.id))

                    return {"success": True, "count": len(downloads)}

            except Exception as e:
                return {"success": False, "error": str(e)}

    try:
        return asyncio.run(_process())
    except Exception as exc:
        raise self.retry(exc=exc)