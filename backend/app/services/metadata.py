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


async def _search_youtube(query: str) -> dict[str, Any]:
    """Search YouTube for the best matching track when direct resolve fails."""
    import yt_dlp
    logger.info(f"Performing enhanced search for: {query}")
    
    def _search() -> dict[str, Any]:
        with yt_dlp.YoutubeDL(_default_opts(extract_flat=True)) as ydl:
            return ydl.extract_info(f"ytsearch1:{query}", download=False)

    try:
        info = await asyncio.to_thread(_search)
        if not info or not info.get("entries"):
            return {"kind": "invalid", "error": "Nenhum resultado encontrado no YouTube"}
        
        entry = info["entries"][0]
        with yt_dlp.YoutubeDL(_default_opts()) as ydl:
            full_info = ydl.extract_info(entry.get("url") or entry.get("webpage_url"), download=False)
            
        return {
            "kind": "track",
            "title": full_info.get("title") or "Untitled",
            "artist": full_info.get("artist") or full_info.get("uploader") or "Unknown",
            "album": full_info.get("album") or "",
            "cover_url": full_info.get("thumbnail") or "",
            "duration": full_info.get("duration") or 0,
            "release_date": full_info.get("release_date") or "",
            "url": full_info.get("webpage_url"),
        }
    except Exception as e:
        logger.error(f"Enhanced search failed: {e}")
        return {"kind": "invalid", "error": f"Falha na busca: {str(e)}"}

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
        logger.warning("Direct resolve failed: %s", error_msg)
        
        if "spotify" in url.lower() or "sign in" in error_msg.lower() or "bot" in error_msg.lower():
            inv_res = await _resolve_via_invidious(url)
            if inv_res.get("kind") != "invalid":
                return inv_res
            return await _search_youtube(url)
            
        return {"kind": "invalid", "error": f"Erro interno: {error_msg}"}

    if not info:
        return {"kind": "invalid", "error": "Nenhum conteúdo encontrado"}

    if "spotify" in url.lower() and info.get("extractor") == "spotify":
        query = f"{info.get('artist', '')} {info.get('title', '')}".strip()
        if query:
            logger.info(f"Spotify metadata found. Searching YouTube for: {query}")
            search_res = await _search_youtube(query)
            if search_res.get("kind") != "invalid":
                return search_res

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
