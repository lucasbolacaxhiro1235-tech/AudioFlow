from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj
from app.models import Download, DownloadStatus, Song
from app.schemas import DownloadCreate, DownloadResponse, PaginatedResponse
from app.workers.tasks import process_download_task, process_playlist_task

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("", response_model=PaginatedResponse)
async def list_downloads(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[DownloadStatus] = None,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Download).where(Download.user_id == current_user.id)

    if status_filter:
        query = query.where(Download.status == status_filter)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Download.created_at.desc()).offset(offset).limit(page_size)
    )
    downloads = result.scalars().all()

    return PaginatedResponse(
        items=downloads,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{download_id}", response_model=DownloadResponse)
async def get_download(
    download_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    download = await db.get(Download, download_id)
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    if download.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return download


@router.post("", response_model=DownloadResponse, status_code=status.HTTP_201_CREATED)
async def create_download(
    download_data: DownloadCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    download = Download(
        user_id=current_user.id,
        **download_data.model_dump(),
    )
    db.add(download)
    await db.commit()
    await db.refresh(download)

    process_download_task.delay(str(download.id))

    return download


@router.post("/playlist", response_model=dict)
async def create_playlist_download(
    playlist_url: str,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await process_playlist_task(playlist_url, str(current_user.id))
    return result


@router.delete("/{download_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_download(
    download_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    download = await db.get(Download, download_id)
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    if download.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if download.status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed download")

    download.status = DownloadStatus.FAILED
    download.error_message = "Cancelled by user"
    await db.commit()


@router.get("/{download_id}/file")
async def get_download_file(
    download_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    from app.storage.r2 import r2_storage

    download = await db.get(Download, download_id)
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    if download.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if download.status != DownloadStatus.COMPLETED or not download.r2_key:
        raise HTTPException(status_code=400, detail="File not ready")

    presigned_url = r2_storage.generate_presigned_url(download.r2_key, expiration=3600)
    if not presigned_url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

    return {"url": presigned_url}