import asyncio
import logging
import re
from typing import Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _valid_url(url: str) -> bool:
    return bool(
        re.match(r"^https?://", url.strip())
        and len(url.strip()) <= 2048
        and " " not in url.strip()
    )


def _default_opts(**extra) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": False,
        "extract_flat": True,
        "skip_download": True,
        "socket_timeout": 30,
        "cookiefile": settings.COOKIES_FILE,
        "extractor_args": {
            "youtube": {
                "player_client": ["android_music", "android", "web"],
            }
        },
    }
    opts.update(extra)
    return opts



async def resolve_url(url: str) -> dict[str, Any]:
    import yt_dlp

    if not _valid_url(url):
        return {"kind": "invalid", "error": "URL inválida"}

    def _extract() -> dict[str, Any]:
        with yt_dlp.YoutubeDL(_default_opts()) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await asyncio.to_thread(_extract)
    except Exception as exc:
        error_msg = str(exc)
        logger.error("Resolve failed detailed: %s", error_msg, exc_info=True)
        return {"kind": "invalid", "error": f"Erro interno: {error_msg}"}

    if not info:
        return {"kind": "invalid", "error": "Nenhum conteúdo encontrado"}

    entries = info.get("entries") or []
    kind = info.get("_type") or "track"
    if kind in ("playlist", "multi_video") or entries:
        items = []
        for e in entries:
            if e is None:
                continue
            if e.get("url") and not re.match(r"^https?://", e["url"]):
                continue
            items.append(
                {
                    "url": e.get("url") or e.get("webpage_url") or "",
                    "title": e.get("title") or e.get("fulltitle") or "Untitled",
                    "artist": e.get("artist") or e.get("uploader") or e.get("channel") or "",
                }
            )
        return {
            "kind": "playlist" if kind == "playlist" else "album",
            "title": info.get("title") or info.get("playlist_title") or "Playlist",
            "artist": info.get("artist") or info.get("uploader") or "",
            "cover_url": info.get("thumbnail") or (entries[0].get("thumbnail") if entries else None),
            "track_count": len(items),
            "items": items,
        }

    return {
        "kind": "track",
        "title": info.get("title") or "Untitled",
        "artist": info.get("artist") or info.get("uploader") or info.get("channel") or "",
        "album": info.get("album") or "",
        "cover_url": info.get("thumbnail") or "",
        "duration": info.get("duration") or 0,
        "release_date": info.get("release_date") or "",
    }


def extract_metadata(url: str) -> dict[str, Any]:
    import yt_dlp

    try:
        with yt_dlp.YoutubeDL(_default_opts(skip_download=True)) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        logger.warning("Metadata extraction failed: %s", exc)
        return {}

    if not info:
        return {}

    artist = (
        info.get("artist")
        or info.get("uploader")
        or info.get("channel")
        or info.get("creator")
        or ""
    )
    album = info.get("album") or ""
    return {
        "title": info.get("title") or info.get("fulltitle") or "Untitled",
        "artist": artist,
        "album": album,
        "cover_url": info.get("thumbnail") or "",
        "duration": info.get("duration") or 0,
        "release_date": info.get("release_date") or info.get("release_year") or "",
        "genre": info.get("genre") or "",
        "source_url": url,
    }


async def validate_url(url: str) -> tuple[bool, str]:
    if not _valid_url(url):
        return False, "URL inválida"
    return True, ""