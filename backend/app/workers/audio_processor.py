import asyncio
import logging
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

from app.config import settings
from app.storage import storage

logger = logging.getLogger(__name__)

# Progress publishing via Redis (thread-safe from yt-dlp hooks)
_redis_pub = None


def _get_redis():
    global _redis_pub
    if _redis_pub is None:
        try:
            import redis as redis_lib

            _redis_pub = redis_lib.Redis.from_url(settings.REDIS_URL, socket_timeout=1)
            _redis_pub.ping()
        except Exception:
            _redis_pub = False
    return _redis_pub if _redis_pub else None


def publish_progress(download_id: Any, data: dict) -> None:
    client = _get_redis()
    if not client:
        return
    try:
        client.hset(f"download:progress:{download_id}", mapping=data)
        client.expire(f"download:progress:{download_id}", 3600)
    except Exception:
        pass


class AudioProcessor:
    async def process_download(self, download_id: uuid.UUID) -> bool:
        from app.database import AsyncSessionLocal
        from app.models import Download, DownloadItem, DownloadStatus

        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download is None or download.status == DownloadStatus.CANCELLED:
                return False
            download.status = DownloadStatus.PROCESSING
            download.stage = "preparing"
            await db.commit()

            items_result = await db.execute(
                __import__("sqlalchemy").select(DownloadItem).where(
                    DownloadItem.download_id == download.id
                )
            )
            items = list(items_result.scalars().all())
            fmt = download.format or settings.AUDIO_OUTPUT_FORMAT
            quality = download.quality or settings.AUDIO_QUALITY
            user_id = str(download.user_id)

        try:
            total_items = max(1, len(items))
            produced_files: list[uuid.UUID] = []

            if items:
                for idx, item in enumerate(items):
                    if item.status.value == "failed":
                        continue
                    self._set_stage(download_id, f"downloading_{idx + 1}_{total_items}")
                    file_id = await self._process_track(
                        download_id, item.url, fmt, quality, user_id
                    )
                    if file_id is not None:
                        produced_files.append(file_id)
                        await self._mark_item(item.id, "completed", file_id=file_id)
                    else:
                        await self._mark_item(item.id, "failed")
                    base = int((idx + 1) / total_items * 100)
                    self._publish(download_id, progress=base, stage="processing")
            else:
                self._set_stage(download_id, "downloading")
                file_id = await self._process_track(download_id, download.url, fmt, quality, user_id)
                if file_id is not None:
                    produced_files.append(file_id)

            await self._complete(download_id, produced_files[0] if produced_files else None)
            return bool(produced_files)

        except Exception as exc:
            logger.exception("Download %s failed", download_id)
            await self._mark_failed(download_id, str(exc))
            return False

    async def _process_track(
        self,
        download_id: uuid.UUID,
        url: str,
        fmt: str,
        quality: str,
        user_id: str,
    ) -> Optional[uuid.UUID]:
        from app.services.metadata import extract_metadata

        meta = await asyncio.to_thread(extract_metadata, url)

        self._publish(
            download_id,
            stage="downloading",
            title=meta.get("title"),
            artist=meta.get("artist"),
            cover_url=meta.get("cover_url"),
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            audio_path = await asyncio.to_thread(self._download_audio, url, tmp_path, download_id)
            if audio_path is None:
                raise RuntimeError("Falha ao baixar o áudio")

            self._publish(download_id, stage="converting")
            converted = await asyncio.to_thread(self._convert_audio, audio_path, tmp_path, fmt, quality)
            if converted is None:
                raise RuntimeError("Falha na conversão de áudio")

            self._publish(download_id, stage="tagging")
            cover_path = await asyncio.to_thread(self._download_cover, meta.get("cover_url"), tmp_path)
            if cover_path is not None:
                await asyncio.to_thread(self._embed_cover, converted, cover_path, fmt)

            self._publish(download_id, stage="uploading")
            file_id = await self._store_file(
                download_id, converted, fmt, meta, user_id
            )
            return file_id

    def _download_audio(self, url: str, tmp_path: Path, download_id: uuid.UUID) -> Optional[Path]:
        import yt_dlp

        outtmpl = str(tmp_path / "%(title)s.%(ext)s")
        opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 30,
            "cookiefile": settings.COOKIES_FILE,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"],
                }
            },
            "progress_hooks": [lambda d: self._hook(d, download_id)],
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as exc:
            logger.warning("yt-dlp failed for %s: %s", url, exc)
            return None

        for candidate in tmp_path.iterdir():
            if candidate.is_file() and candidate.suffix.lower() in (
                ".webm", ".m4a", ".mp3", ".opus", ".flac", ".wav", ".ogg", ".aac",
            ):
                return candidate
        return None

    def _hook(self, d: dict, download_id: uuid.UUID) -> None:
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes") or 0
            speed = d.get("speed")
            data = {"stage": "downloading", "downloaded_bytes": downloaded}
            if total:
                data["total_bytes"] = total
                data["progress"] = min(90, int((downloaded / total) * 90))
            if speed:
                data["speed_bps"] = int(speed)
            publish_progress(download_id, data)

    def _convert_audio(self, input_path: Path, tmp_path: Path, fmt: str, quality: str) -> Optional[Path]:
        output = tmp_path / f"converted.{fmt}"
        codec_map = {
            "mp3": "libmp3lame",
            "m4a": "aac",
            "opus": "libopus",
            "flac": "flac",
            "wav": "pcm_s16le",
        }
        codec = codec_map.get(fmt, "copy")
        cmd = [settings.FFMPEG_PATH, "-y", "-i", str(input_path), "-vn"]
        if fmt in ("mp3", "m4a", "opus"):
            bitrate = quality if quality.endswith("k") else settings.AUDIO_QUALITY
            cmd += ["-codec:a", codec, "-b:a", bitrate]
        else:
            cmd += ["-codec:a", codec]
        cmd += ["-map_metadata", "0", str(output)]

        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=1200)
            if proc.returncode != 0:
                logger.warning("FFmpeg error: %s", proc.stderr.decode(errors="ignore")[-500:])
                return None
            return output
        except Exception as exc:
            logger.warning("FFmpeg exception: %s", exc)
            return None

    def _download_cover(self, url: Optional[str], tmp_path: Path) -> Optional[Path]:
        if not url:
            return None
        try:
            import httpx

            resp = httpx.get(url, timeout=20, follow_redirects=True)
            if resp.status_code != 200:
                return None
            path = tmp_path / "cover.jpg"
            path.write_bytes(resp.content)
            return path
        except Exception:
            return None

    def _embed_cover(self, audio_path: Path, cover_path: Path, fmt: str) -> None:
        if fmt not in ("mp3", "m4a", "opus"):
            return
        tmp_out = audio_path.with_name(audio_path.stem + "_with_cover." + fmt)
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-i", str(audio_path),
            "-i", str(cover_path),
            "-map", "0:a", "-map", "1:v",
            "-c:v", "mjpeg", "-disposition:v", "attached_pic",
            "-id3v2_version", "3",
            str(tmp_out),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=300)
            if proc.returncode == 0:
                tmp_out.replace(audio_path)
        except Exception:
            pass

    async def _store_file(
        self,
        download_id: uuid.UUID,
        audio_path: Path,
        fmt: str,
        meta: dict,
        user_id: str,
    ) -> uuid.UUID:
        from app.database import AsyncSessionLocal
        from app.models import File, AudioMetadata, StorageBackend
        from app.services.usage import add_storage_bytes

        size = audio_path.stat().st_size
        file_name = audio_path.name
        key = storage.generate_key("songs", user_id, file_name) if hasattr(storage, "generate_key") else f"songs/{user_id}/{file_name}"

        with open(audio_path, "rb") as f:
            ok = storage.upload_fileobj(f, key, content_type=f"audio/{fmt}")

        if not ok:
            raise RuntimeError("Falha ao enviar arquivo ao storage")

        mime_map = {"mp3": "audio/mpeg", "m4a": "audio/mp4", "opus": "audio/opus", "flac": "audio/flac", "wav": "audio/wav"}
        file_obj = File(
            user_id=uuid.UUID(user_id),
            storage=StorageBackend(storage.name),
            object_key=key,
            file_name=file_name,
            mime_type=mime_map.get(fmt, "audio/mpeg"),
            format=fmt,
            size_bytes=size,
        )
        meta_obj = AudioMetadata(
            file_id=file_obj.id,
            title=meta.get("title") or "Untitled",
            artist=meta.get("artist") or "Unknown Artist",
            album=meta.get("album") or "",
            duration_seconds=meta.get("duration") or 0,
            cover_url=meta.get("cover_url") or "",
            bitrate=int((meta.get("abr") or 0)),
            genre=meta.get("genre") or "",
            release_date=str(meta.get("release_date") or ""),
            source_url=meta.get("source_url") or "",
        )
        meta_obj.file = file_obj
        file_obj.audio_metadata = meta_obj

        async with AsyncSessionLocal() as db:
            db.add(file_obj)
            await db.flush()
            await add_storage_bytes(db, uuid.UUID(user_id), size)

        return file_obj.id

    def _publish(self, download_id: uuid.UUID, **data) -> None:
        publish_progress(download_id, data)

    def _set_stage(self, download_id: uuid.UUID, stage: str) -> None:
        publish_progress(download_id, {"stage": stage})

    async def _mark_item(self, item_id: uuid.UUID, status: str, file_id: Optional[uuid.UUID] = None) -> None:
        from app.database import AsyncSessionLocal
        from app.models import DownloadItem, DownloadItemStatus

        async with AsyncSessionLocal() as db:
            item = await db.get(DownloadItem, item_id)
            if item is not None:
                item.status = DownloadItemStatus(status)
                if file_id:
                    item.file_id = file_id
                await db.commit()

    async def _complete(self, download_id: uuid.UUID, file_id: Optional[uuid.UUID]) -> None:
        from app.database import AsyncSessionLocal
        from app.models import Download, DownloadStatus
        from datetime import datetime, timezone

        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download is not None:
                download.status = DownloadStatus.COMPLETED
                download.progress = 100
                download.stage = "completed"
                download.file_id = file_id
                download.completed_at = datetime.now(timezone.utc)
                await db.commit()
        self._publish(download_id, status="completed", progress=100, stage="completed", file_id=str(file_id) if file_id else None)

    async def _mark_failed(self, download_id: uuid.UUID, error: str) -> None:
        from app.database import AsyncSessionLocal
        from app.models import Download, DownloadStatus

        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download is not None:
                download.status = DownloadStatus.FAILED
                download.error_message = error[:500]
                download.stage = "failed"
                await db.commit()
        self._publish(download_id, status="failed", stage="failed", error_message=error[:500])


audio_processor = AudioProcessor()