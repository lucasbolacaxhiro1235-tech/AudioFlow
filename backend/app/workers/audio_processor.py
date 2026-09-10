import asyncio
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID
import yt_dlp
from app.config import settings
from app.storage.r2 import r2_storage
from app.database import AsyncSessionLocal
from app.models import Download, DownloadStatus, Song, Artist, Album
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class AudioProcessor:
    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": False,
        }

    async def process_download(self, download_id: UUID) -> bool:
        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if not download:
                return False

            download.status = DownloadStatus.PROCESSING
            download.progress = 10
            await db.commit()

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                audio_path = await self._download_audio(download.spotify_url, tmpdir_path, download_id)
                if not audio_path:
                    await self._mark_failed(download_id, "Failed to download audio")
                    return False

                await self._update_progress(download_id, 50)

                processed_path = await self._convert_audio(audio_path, tmpdir_path)
                if not processed_path:
                    await self._mark_failed(download_id, "Failed to convert audio")
                    return False

                await self._update_progress(download_id, 70)

                file_size = processed_path.stat().st_size
                r2_key = r2_storage.generate_audio_key(str(download.user_id), processed_path.name)

                with open(processed_path, "rb") as f:
                    success = r2_storage.upload_file(
                        f,
                        r2_key,
                        content_type=f"audio/{settings.AUDIO_OUTPUT_FORMAT}",
                        metadata={"download_id": str(download_id)},
                    )

                if not success:
                    await self._mark_failed(download_id, "Failed to upload to R2")
                    return False

                await self._update_progress(download_id, 90)

                song = await self._create_or_get_song(download, r2_key, file_size, processed_path)
                if not song:
                    await self._mark_failed(download_id, "Failed to create song record")
                    return False

                await self._complete_download(download_id, song.id, r2_key, file_size)
                return True

        except Exception as e:
            print(f"Processing error for download {download_id}: {e}")
            await self._mark_failed(download_id, str(e))
            return False

    async def _download_audio(self, spotify_url: str, tmpdir: Path, download_id: UUID) -> Optional[Path]:
        output_template = tmpdir / "%(title)s.%(ext)s"

        ydl_opts = self.ydl_opts.copy()
        ydl_opts.update({
            "outtmpl": str(output_template),
            "progress_hooks": [lambda d: self._progress_hook(d, download_id)],
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(spotify_url, download=True)
                if info:
                    for file in tmpdir.iterdir():
                        if file.suffix in [".webm", ".m4a", ".mp3", ".opus", ".flac", ".wav"]:
                            return file
        except Exception as e:
            print(f"yt-dlp error: {e}")
        return None

    def _progress_hook(self, d: dict, download_id: UUID):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                percent = int((d.get("downloaded_bytes", 0) / total) * 40)
                asyncio.create_task(self._update_progress(download_id, 10 + percent))

    async def _convert_audio(self, input_path: Path, tmpdir: Path) -> Optional[Path]:
        output_path = tmpdir / f"converted.{settings.AUDIO_OUTPUT_FORMAT}"

        cmd = [
            settings.FFMPEG_PATH,
            "-y",
            "-i", str(input_path),
            "-codec:a", "libmp3lame" if settings.AUDIO_OUTPUT_FORMAT == "mp3" else "copy",
            "-b:a", settings.AUDIO_QUALITY,
            "-map_metadata", "0",
            "-id3v2_version", "3",
            str(output_path),
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                print(f"FFmpeg error: {stderr.decode()}")
                return None

            return output_path
        except Exception as e:
            print(f"Conversion error: {e}")
            return None

    async def _create_or_get_song(
        self, download: Download, r2_key: str, file_size: int, audio_path: Path
    ) -> Optional[Song]:
        async with AsyncSessionLocal() as db:
            if download.song_id:
                song = await db.get(Song, download.song_id)
                if song:
                    song.audio_url = r2_storage.get_public_url(r2_key)
                    song.r2_key = r2_key
                    song.file_size = file_size
                    song.format = settings.AUDIO_OUTPUT_FORMAT
                    await db.commit()
                    await db.refresh(song)
                    return song

            ydl_opts = {"quiet": True, "skip_download": True}
            metadata = {}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(download.spotify_url, download=False)
                    if info:
                        metadata = {
                            "title": info.get("title", "Unknown"),
                            "artist": info.get("artist", info.get("uploader", "Unknown Artist")),
                            "album": info.get("album", "Unknown Album"),
                            "duration": info.get("duration", 0),
                            "thumbnail": info.get("thumbnail"),
                            "spotify_id": self._extract_spotify_id(download.spotify_url),
                        }
            except Exception as e:
                print(f"Metadata extraction error: {e}")

            artist = await self._get_or_create_artist(db, metadata.get("artist", "Unknown Artist"))
            album = await self._get_or_create_album(db, artist.id, metadata.get("album", "Unknown Album"), metadata.get("thumbnail"))

            song = Song(
                title=metadata.get("title", "Unknown"),
                artist_id=artist.id,
                album_id=album.id if album else None,
                duration=metadata.get("duration", 0),
                cover_url=metadata.get("thumbnail") or album.cover_url if album else None,
                audio_url=r2_storage.get_public_url(r2_key),
                r2_key=r2_key,
                format=settings.AUDIO_OUTPUT_FORMAT,
                bitrate=int(settings.AUDIO_QUALITY.replace("k", "")) * 1000,
                file_size=file_size,
                spotify_id=metadata.get("spotify_id"),
            )

            db.add(song)
            await db.commit()
            await db.refresh(song)
            return song

    def _extract_spotify_id(self, url: str) -> Optional[str]:
        import re
        match = re.search(r"spotify\.com/(?:track|album|artist)/([a-zA-Z0-9]+)", url)
        return match.group(1) if match else None

    async def _get_or_create_artist(self, db: AsyncSession, name: str) -> Artist:
        result = await db.execute(select(Artist).where(Artist.name == name))
        artist = result.scalar_one_or_none()
        if artist:
            return artist

        artist = Artist(name=name)
        db.add(artist)
        await db.commit()
        await db.refresh(artist)
        return artist

    async def _get_or_create_album(
        self, db: AsyncSession, artist_id: UUID, name: str, cover_url: Optional[str]
    ) -> Optional[Album]:
        if not name or name == "Unknown Album":
            return None

        result = await db.execute(select(Album).where(Album.title == name, Album.artist_id == artist_id))
        album = result.scalar_one_or_none()
        if album:
            return album

        album = Album(title=name, artist_id=artist_id, cover_url=cover_url)
        db.add(album)
        await db.commit()
        await db.refresh(album)
        return album

    async def _update_progress(self, download_id: UUID, progress: int):
        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download:
                download.progress = min(100, progress)
                await db.commit()

    async def _mark_failed(self, download_id: UUID, error: str):
        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download:
                download.status = DownloadStatus.FAILED
                download.error_message = error
                await db.commit()

    async def _complete_download(self, download_id: UUID, song_id: UUID, r2_key: str, file_size: int):
        async with AsyncSessionLocal() as db:
            download = await db.get(Download, download_id)
            if download:
                download.status = DownloadStatus.COMPLETED
                download.progress = 100
                download.song_id = song_id
                download.r2_key = r2_key
                download.file_size = file_size
                download.completed_at = __import__("datetime").datetime.utcnow()
                await db.commit()


audio_processor = AudioProcessor()