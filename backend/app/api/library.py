import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.database import get_db
from app.models import AudioMetadata, File, PlaylistItem, User
from app.schemas import FileResponse, MessageResponse, PaginatedResponse
from app.services.usage import remove_storage_bytes
from app.storage import storage

router = APIRouter(prefix="/library", tags=["library"])


def _file_response(f: File) -> FileResponse:
    resp = FileResponse.model_validate(f)
    resp.download_url = storage.presigned_url(f.object_key, expiration=3600) or storage.public_url(
        f.object_key
    )
    return resp


@router.get("", response_model=PaginatedResponse[FileResponse])
async def list_library(
    page: int = 1,
    page_size: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if page_size > 200:
        page_size = 200
    offset = (page - 1) * page_size

    total = (
        await db.execute(
            select(func.count()).select_from(File).where(File.user_id == user.id, File.deleted_at.is_(None))
        )
    ).scalar() or 0

    result = await db.execute(
        select(File)
        .options(selectinload(File.audio_metadata))
        .where(File.user_id == user.id, File.deleted_at.is_(None))
        .order_by(File.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [_file_response(f) for f in result.scalars().all()]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(File).options(selectinload(File.audio_metadata)).where(File.id == file_id)
    )
    f = result.scalar_one_or_none()
    if f is None or f.user_id != user.id or f.deleted_at is not None:
        raise HTTPException(status_code=404, detail="File not found")
    return _file_response(f)


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    f = await db.get(File, file_id)
    if f is None or f.user_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")

    storage.delete(f.object_key)
    await db.execute(
        PlaylistItem.__table__.delete().where(PlaylistItem.file_id == f.id)
    )
    await remove_storage_bytes(db, user.id, f.size_bytes)
    await db.delete(f)
    await db.commit()
    return MessageResponse(message="File deleted")