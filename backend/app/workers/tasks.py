import asyncio
import uuid

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
    worker_max_tasks_per_child=50,
    result_expires=86400,
    task_routes={
        "app.workers.tasks.process_download": {"queue": "downloads"},
    },
    beat_schedule={},
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_download_task(self, download_id: str):
    from app.workers.audio_processor import audio_processor

    try:
        result = asyncio.run(audio_processor.process_download(uuid.UUID(download_id)))
        return {"success": result, "download_id": download_id}
    except Exception as exc:
        raise self.retry(exc=exc)