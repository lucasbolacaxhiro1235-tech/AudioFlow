from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj, get_current_user
from app.models import Playlist, Song, Favorite, playlist_songs
from app.schemas import (
    PlaylistCreate, PlaylistUpdate, PlaylistResponse, PlaylistWithSongs,
    SongWithRelations, PaginatedResponse, ErrorResponse
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=PaginatedResponse)
async def list_playlists(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = None,
    is_public: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Playlist).options(selectinload(Playlist.owner))

    if user_id:
        query = query.where(Playlist.owner_id == user_id)
    if is_public is not None:
        query = query.where(Playlist.is_public == is_public)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Playlist.updated_at.desc()).offset(offset).limit(page_size)
    )
    playlists = result.scalars().all()

    return PaginatedResponse(
        items=playlists,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/featured", response_model=List[PlaylistResponse])
async def get_featured_playlists(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .options(selectinload(Playlist.owner))
        .where(Playlist.is_public == True)
        .order_by(Playlist.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{playlist_id}", response_model=PlaylistWithSongs)
async def get_playlist(
    playlist_id: UUID,
    current_user_id: Optional[UUID] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .options(
            selectinload(Playlist.owner),
            selectinload(Playlist.songs).selectinload(Song.artist),
            selectinload(Playlist.songs).selectinload(Song.album),
        )
        .where(Playlist.id == playlist_id)
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if not playlist.is_public and (not current_user_id or playlist.owner_id != current_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this playlist")

    is_favorite = False
    if current_user_id:
        fav_result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user_id,
                Favorite.playlist_id == playlist_id,
            )
        )
        is_favorite = fav_result.scalar_one_or_none() is not None

    playlist_response = PlaylistWithSongs.model_validate(playlist)
    playlist_response.is_favorite = is_favorite
    return playlist_response


@router.post("", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = Playlist(**playlist_data.model_dump(), owner_id=current_user.id)
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return playlist


@router.patch("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: UUID,
    playlist_data: PlaylistUpdate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this playlist")

    for field, value in playlist_data.model_dump(exclude_unset=True).items():
        setattr(playlist, field, value)

    await db.commit()
    await db.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this playlist")

    await db.delete(playlist)
    await db.commit()


@router.post("/{playlist_id}/songs", status_code=status.HTTP_204_NO_CONTENT)
async def add_song_to_playlist(
    playlist_id: UUID,
    song_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id, options=[selectinload(Playlist.songs)])
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id and not playlist.is_collaborative:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")

    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    if song in playlist.songs:
        raise HTTPException(status_code=400, detail="Song already in playlist")

    playlist.songs.append(song)
    playlist.total_tracks = len(playlist.songs)
    playlist.total_duration = sum(s.duration for s in playlist.songs)
    await db.commit()


@router.delete("/{playlist_id}/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_song_from_playlist(
    playlist_id: UUID,
    song_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id, options=[selectinload(Playlist.songs)])
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id and not playlist.is_collaborative:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")

    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    if song not in playlist.songs:
        raise HTTPException(status_code=400, detail="Song not in playlist")

    playlist.songs.remove(song)
    playlist.total_tracks = len(playlist.songs)
    playlist.total_duration = sum(s.duration for s in playlist.songs)
    await db.commit()


@router.put("/{playlist_id}/songs/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_playlist_songs(
    playlist_id: UUID,
    song_ids: List[UUID],
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    playlist = await db.get(Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this playlist")

    await db.execute(
        delete(playlist_songs).where(playlist_songs.c.playlist_id == playlist_id)
    )

    for position, song_id in enumerate(song_ids):
        await db.execute(
            playlist_songs.insert().values(
                playlist_id=playlist_id,
                song_id=song_id,
                position=position,
            )
        )

    playlist.total_tracks = len(song_ids)
    await db.commit()