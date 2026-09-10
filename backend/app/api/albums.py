from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj
from app.models import Album, Song, Artist
from app.schemas import AlbumCreate, AlbumUpdate, AlbumResponse, SongWithRelations, PaginatedResponse

router = APIRouter(prefix="/albums", tags=["albums"])


@router.get("", response_model=PaginatedResponse)
async def list_albums(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    artist_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Album).options(selectinload(Album.artist))

    if artist_id:
        query = query.where(Album.artist_id == artist_id)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            Album.title.ilike(search_term) | Album.spotify_id.ilike(search_term)
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Album.release_date.desc().nullslast()).offset(offset).limit(page_size)
    )
    albums = result.scalars().all()

    return PaginatedResponse(
        items=albums,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/popular", response_model=List[AlbumResponse])
async def get_popular_albums(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album)
        .options(selectinload(Album.artist))
        .order_by(Album.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Album)
        .options(selectinload(Album.artist))
        .where(Album.id == album_id)
    )
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@router.get("/{album_id}/songs", response_model=List[SongWithRelations])
async def get_album_songs(
    album_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .where(Song.album_id == album_id)
        .order_by(Song.id)
    )
    return result.scalars().all()


@router.post("", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(
    album_data: AlbumCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    album = Album(**album_data.model_dump())
    db.add(album)
    await db.commit()
    await db.refresh(album)
    return album


@router.patch("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: UUID,
    album_data: AlbumUpdate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    for field, value in album_data.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    await db.commit()
    await db.refresh(album)
    return album


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    album = await db.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    await db.delete(album)
    await db.commit()