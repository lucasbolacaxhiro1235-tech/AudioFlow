import asyncio
import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_user_plan
from app.core.rate_limit import rate_limit
from app.database import get_db
from app.models import Download, DownloadItem, DownloadStatus, User
from app.schemas import (
    DownloadCreate,
    DownloadItemResponse,
    DownloadResponse,
    MessageResponse,
    PaginatedResponse,
)
from app.services import metadata as metadata_service
from app.services.usage import can_initiate_download, increment_download_count
from app.storage import storage

router = APIRouter(prefix="/downloads", tags=["downloads"])

ACTIVE_STATUSES = ["pending", "validating", "processing", "converting"]


def _download_response(d: Download) -> DownloadResponse:
    resp = DownloadResponse.model_validate(d)
    return resp


def _enqueue(download_id: uuid.UUID) -> bool:
    try:
        from app.workers.tasks import process_download_task

        process_download_task.delay(str(download_id))
        return True
    except Exception:
        return False


@router.post("/resolve", response_model=dict)
async def resolve(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await rate_limit(request, limit=30, window=60)
    body = await request.json()
    url = body.get("url", "")
    result = await metadata_service.resolve_url(url)
    return result


@router.post("", response_model=DownloadResponse, status_code=status.HTTP_201_CREATED)
async def create_download(
    payload: DownloadCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await rate_limit(request, limit=30, window=60)
    valid, err = await metadata_service.validate_url(payload.url)
    if not valid:
        raise HTTPException(status_code=422, detail=err)

    plan = await get_user_plan(db, user.id)
    ok, reason = await can_initiate_download(db, user.id, plan)
    if not ok:
        raise HTTPException(status_code=429, detail=reason)

    resolved = await metadata_service.resolve_url(payload.url)
    if resolved.get("kind") == "invalid":
        raise HTTPException(status_code=422, detail=resolved.get("error", "URL inválida"))

    fmt = payload.format
    quality = payload.quality or ("320k" if fmt == "mp3" else "best")

    download = Download(
        user_id=user.id,
        url=payload.url,
        kind=resolved.get("kind", "track"),
        title=resolved.get("title"),
        artist=resolved.get("artist"),
        album=resolved.get("album"),
        cover_url=resolved.get("cover_url"),
        format=fmt,
        quality=quality,
        status=DownloadStatus.PENDING,
        stage="queued",
    )
    db.add(download)
    await db.flush()

    items = resolved.get("items") or []
    item_objs = []
    for i, item in enumerate(items):
        if not item.get("url"):
            continue
        item_objs.append(
            DownloadItem(
                download_id=download.id,
                url=item["url"],
                title=item.get("title"),
                artist=item.get("artist"),
                position=i,
            )
        )
    if item_objs:
        db.add_all(item_objs)

    await db.commit()
    await db.refresh(download)

    if not _enqueue(download.id):
        from app.workers.audio_processor import audio_processor

        async def _run():
            await audio_processor.process_download(download.id)

        background_tasks.add_task(_run)

    download = await _load_download(db, download.id)
    return _download_response(download)


async def _load_download(db: AsyncSession, download_id: uuid.UUID) -> Download:
    result = await db.execute(
        select(Download)
        .options(selectinload(Download.items))
        .where(Download.id == download_id)
    )
    return result.scalar_one_or_none()


@router.get("", response_model=PaginatedResponse[DownloadResponse])
async def list_downloads(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if page_size > 100:
        page_size = 100
    offset = (page - 1) * page_size

    total = (
        await db.execute(select(func.count()).select_from(Download).where(Download.user_id == user.id))
    ).scalar() or 0

    result = await db.execute(
        select(Download)
        .options(selectinload(Download.items))
        .where(Download.user_id == user.id)
        .order_by(Download.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [_download_response(d) for d in result.scalars().all()]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{download_id}", response_model=DownloadResponse)
async def get_download(
    download_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    download = await _load_download(db, download_id)
    if download is None or download.user_id != user.id:
        raise HTTPException(status_code=404, detail="Download not found")
    return _download_response(download)


@router.delete("/{download_id}", response_model=MessageResponse)
async def cancel_download(
    download_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    download = await db.get(Download, download_id)
    if download is None or download.user_id != user.id:
        raise HTTPException(status_code=404, detail="Download not found")
    if download.status in (DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED):
        raise HTTPException(status_code=400, detail="Cannot cancel this download")
    download.status = DownloadStatus.CANCELLED
    download.stage = "cancelled"
    await db.commit()
    return MessageResponse(message="Download cancelled")


@router.get("/{download_id}/events")
async def download_events(
    download_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    from app.config import settings as cfg
    from app.core.deps import _get_guest_user
    from app.core.security import decode_token
    from app.schemas import TokenType

    token = request.query_params.get("token", "")
    client_id = request.query_params.get("client_id", "")

    user: User | None = None
    if token:
        token_data = decode_token(token)
        if token_data and token_data.token_type == TokenType.ACCESS:
            user = await db.get(User, token_data.user_id)
    elif client_id and cfg.ALLOW_ANONYMOUS:
        try:
            str(uuid.UUID(client_id))
        except ValueError:
            client_id = ""
        if client_id:
            user = await _get_guest_user(db, client_id)

    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")

    download = await db.get(Download, download_id)
    if download is None or download.user_id != user.id:
        raise HTTPException(status_code=404, detail="Download not found")

    async def event_stream():
        last = None
        try:
            while True:
                d = await _load_download(db, download_id)
                if d is None:
                    break
                payload = {
                    "status": d.status.value,
                    "progress": d.progress,
                    "downloaded_bytes": d.downloaded_bytes,
                    "total_bytes": d.total_bytes,
                    "speed_bps": d.speed_bps,
                    "stage": d.stage,
                    "error_message": d.error_message,
                    "file_id": str(d.file_id) if d.file_id else None,
                }
                if payload != last:
                    last = payload
                    yield f"data: {json.dumps(payload)}\n\n"
                if d.status in (DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED):
                    break
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{download_id}/file")
async def get_download_file(
    download_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    download = await db.get(Download, download_id)
    if download is None or download.user_id != user.id:
        raise HTTPException(status_code=404, detail="Download not found")

    from app.models import File

    file_obj = await db.get(File, download.file_id) if download.file_id else None
    if file_obj is None or download.status != DownloadStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File not ready")

    url = storage.presigned_url(file_obj.object_key, expiration=3600)
    if not url:
        url = storage.public_url(file_obj.object_key)
    return {"url": url, "file_name": file_obj.file_name}