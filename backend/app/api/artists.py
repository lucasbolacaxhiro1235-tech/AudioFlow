from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj
from app.models import Artist, Song, Album
from app.schemas import ArtistCreate, ArtistUpdate, ArtistResponse, SongWithRelations, AlbumResponse, PaginatedResponse

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("", response_model=PaginatedResponse)
async def list_artists(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Artist)

    if search:
        search_term = f"%{search}%"
        query = query.where(Artist.name.ilike(search_term))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Artist.followers_count.desc()).offset(offset).limit(page_size)
    )
    artists = result.scalars().all()

    return PaginatedResponse(
        items=artists,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/featured", response_model=List[ArtistResponse])
async def get_featured_artists(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Artist)
        .order_by(Artist.followers_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.get("/{artist_id}/songs", response_model=List[SongWithRelations])
async def get_artist_songs(
    artist_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .where(Song.artist_id == artist_id)
        .order_by(Song.play_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{artist_id}/albums", response_model=List[AlbumResponse])
async def get_artist_albums(
    artist_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    result = await db.execute(
        select(Album)
        .where(Album.artist_id == artist_id)
        .order_by(Album.release_date.desc().nullslast())
    )
    return result.scalars().all()


@router.post("", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED)
async def create_artist(
    artist_data: ArtistCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    artist = Artist(**artist_data.model_dump())
    db.add(artist)
    await db.commit()
    await db.refresh(artist)
    return artist


@router.patch("/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: UUID,
    artist_data: ArtistUpdate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    for field, value in artist_data.model_dump(exclude_unset=True).items():
        setattr(artist, field, value)

    await db.commit()
    await db.refresh(artist)
    return artist


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(
    artist_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    artist = await db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    await db.delete(artist)
    await db.commit()