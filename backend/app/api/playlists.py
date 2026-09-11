import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.database import get_db
from app.models import File, Playlist, PlaylistItem, User
from app.schemas import (
    MessageResponse,
    PlaylistCreate,
    PlaylistItemAdd,
    PlaylistItemResponse,
    PlaylistResponse,
    PlaylistSummary,
    PlaylistUpdate,
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


async def _summary(db: AsyncSession, p: Playlist) -> PlaylistSummary:
    track_count = len(p.items)
    total_size = 0
    for item in p.items:
        if item.file:
            total_size += item.file.size_bytes
    return PlaylistSummary(
        id=p.id,
        name=p.name,
        description=p.description,
        cover_url=p.cover_url,
        is_public=p.is_public,
        track_count=track_count,
        total_size_bytes=total_size,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


async def _load_playlist(db: AsyncSession, playlist_id: uuid.UUID) -> Playlist | None:
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.items).selectinload(PlaylistItem.file).selectinload(File.audio_metadata))
        .where(Playlist.id == playlist_id)
    )
    return result.scalar_one_or_none()


def _to_response(p: Playlist) -> PlaylistResponse:
    total_size = 0
    items = []
    for item in p.items:
        if item.file:
            total_size += item.file.size_bytes
        from app.schemas import FileResponse

        fr = FileResponse.model_validate(item.file) if item.file else None
        items.append(
            PlaylistItemResponse(
                id=item.id,
                position=item.position,
                added_at=item.created_at,
                file=fr,
            )
        )
    return PlaylistResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        cover_url=p.cover_url,
        is_public=p.is_public,
        track_count=len(items),
        total_size_bytes=total_size,
        created_at=p.created_at,
        updated_at=p.updated_at,
        items=items,
    )


@router.get("", response_model=list[PlaylistSummary])
async def list_playlists(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.items).selectinload(PlaylistItem.file))
        .where(Playlist.user_id == user.id)
        .order_by(Playlist.created_at.desc())
    )
    return [await _summary(db, p) for p in result.scalars().all()]


@router.post("", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    payload: PlaylistCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = Playlist(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        cover_url=payload.cover_url,
        is_public=payload.is_public,
    )
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return _to_response(await _load_playlist(db, playlist.id))


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(
    playlist_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await _load_playlist(db, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return _to_response(playlist)


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: uuid.UUID,
    payload: PlaylistUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if payload.name is not None:
        playlist.name = payload.name
    if payload.description is not None:
        playlist.description = payload.description
    if payload.cover_url is not None:
        playlist.cover_url = payload.cover_url
    if payload.is_public is not None:
        playlist.is_public = payload.is_public
    await db.commit()
    return _to_response(await _load_playlist(db, playlist_id))


@router.delete("/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    await db.delete(playlist)
    await db.commit()
    return MessageResponse(message="Playlist deleted")


@router.post("/{playlist_id}/items", response_model=PlaylistResponse)
async def add_playlist_item(
    playlist_id: uuid.UUID,
    payload: PlaylistItemAdd,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    f = await db.get(File, payload.file_id)
    if f is None or f.user_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")

    existing = await db.execute(
        select(PlaylistItem).where(
            PlaylistItem.playlist_id == playlist_id, PlaylistItem.file_id == payload.file_id
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="File already in playlist")

    max_pos = (
        await db.execute(
            select(func.max(PlaylistItem.position)).where(PlaylistItem.playlist_id == playlist_id)
        )
    ).scalar() or -1

    db.add(PlaylistItem(playlist_id=playlist_id, file_id=payload.file_id, position=max_pos + 1))
    await db.commit()
    return _to_response(await _load_playlist(db, playlist_id))


@router.delete("/{playlist_id}/items/{item_id}", response_model=PlaylistResponse)
async def remove_playlist_item(
    playlist_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    item = await db.get(PlaylistItem, item_id)
    if item is None or item.playlist_id != playlist_id:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()
    return _to_response(await _load_playlist(db, playlist_id))


@router.put("/{playlist_id}/items/reorder", response_model=PlaylistResponse)
async def reorder_playlist_items(
    playlist_id: uuid.UUID,
    item_ids: list[uuid.UUID],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if playlist is None or playlist.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")

    result = await db.execute(select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id))
    items = {str(i.id): i for i in result.scalars().all()}
    for pos, item_id in enumerate(item_ids):
        item = items.get(str(item_id))
        if item:
            item.position = pos
    await db.commit()
    return _to_response(await _load_playlist(db, playlist_id))