import asyncio
import logging
import re
import httpx
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
        "socket_timeout": 15,
        "cookiefile": settings.COOKIES_FILE,
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "android_music", "web"],
            }
        },
    }
    opts.update(extra)
    return opts


async def _resolve_via_invidious(url: str) -> dict[str, Any]:
    """Fallback using Invidious API to bypass YouTube bot detection."""
    instances = [
        "https://invidious.snopyta.org",
        "https://inv.tux.fi",
        "https://invidious.flokinet.to",
    ]
    
    video_id = None
    match = re.search(r"(?:v=|\/embed\/|\/watch\?v=)([a-zA-Z0-9_-]{11})", url)
    if match:
        video_id = match.group(1)
    
    if not video_id:
        return {"kind": "invalid", "error": "Não foi possível extrair o ID do vídeo para fallback"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for instance in instances:
            try:
                logger.info(f"Trying Invidious fallback: {instance}")
                resp = await client.get(f"{instance}/api/v1/videos/{video_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "kind": "track",
                        "title": data.get("title"),
                        "artist": data.get("author"),
                        "album": "",
                        "cover_url": data.get("videoThumbnails", [{}])[-1].get("url"),
                        "duration": data.get("lengthSeconds", 0),
                        "release_date": data.get("published"),
                    }
            except Exception as e:
                logger.warning(f"Invidious instance {instance} failed: {e}")
                continue
    
    return {"kind": "invalid", "error": "Todos os servidores de fallback falharam"}


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
        logger.warning("yt-dlp failed: %s. Attempting Invidious fallback...", error_msg)
        
        if "sign in" in error_msg.lower() or "bot" in error_msg.lower():
            return await _resolve_via_invidious(url)
            
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
