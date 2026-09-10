from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj, get_current_user
from app.models import Song, Artist, Album, Favorite
from app.schemas import (
    SongCreate, SongUpdate, SongResponse, SongWithRelations,
    PaginatedResponse, ErrorResponse
)

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("", response_model=PaginatedResponse)
async def list_songs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    artist_id: Optional[UUID] = None,
    album_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Song).options(
        selectinload(Song.artist),
        selectinload(Song.album),
    )

    if artist_id:
        query = query.where(Song.artist_id == artist_id)
    if album_id:
        query = query.where(Song.album_id == album_id)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Song.title.ilike(search_term),
                Song.spotify_id.ilike(search_term),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Song.created_at.desc()).offset(offset).limit(page_size)
    )
    songs = result.scalars().all()

    return PaginatedResponse(
        items=songs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/popular", response_model=List[SongWithRelations])
async def get_popular_songs(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .order_by(Song.play_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/recent", response_model=List[SongWithRelations])
async def get_recent_songs(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .order_by(Song.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{song_id}", response_model=SongWithRelations)
async def get_song(
    song_id: UUID,
    current_user_id: Optional[UUID] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .where(Song.id == song_id)
    )
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    is_favorite = False
    if current_user_id:
        fav_result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user_id,
                Favorite.song_id == song_id,
            )
        )
        is_favorite = fav_result.scalar_one_or_none() is not None

    song_dict = SongWithRelations.model_validate(song)
    song_dict.is_favorite = is_favorite
    return song_dict


@router.post("", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def create_song(
    song_data: SongCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    song = Song(**song_data.model_dump())
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


@router.patch("/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: UUID,
    song_data: SongUpdate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    for field, value in song_data.model_dump(exclude_unset=True).items():
        setattr(song, field, value)

    await db.commit()
    await db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    await db.delete(song)
    await db.commit()


@router.post("/{song_id}/play", status_code=status.HTTP_204_NO_CONTENT)
async def increment_play_count(
    song_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    song.play_count += 1
    await db.commit()