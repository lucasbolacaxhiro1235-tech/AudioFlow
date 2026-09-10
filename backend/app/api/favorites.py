from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj, get_current_user
from app.models import Favorite, Song, Album, Artist, Playlist
from app.schemas import FavoriteCreate, FavoriteResponse, PaginatedResponse, SongWithRelations, AlbumResponse, ArtistResponse, PlaylistResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=PaginatedResponse)
async def list_favorites(
    type: Optional[str] = Query(None, regex="^(song|album|artist|playlist)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Favorite).where(Favorite.user_id == current_user.id)

    if type == "song":
        query = query.where(Favorite.song_id.isnot(None)).options(
            selectinload(Favorite.song).selectinload(Song.artist),
            selectinload(Favorite.song).selectinload(Song.album),
        )
    elif type == "album":
        query = query.where(Favorite.album_id.isnot(None)).options(
            selectinload(Favorite.album).selectinload(Album.artist),
        )
    elif type == "artist":
        query = query.where(Favorite.artist_id.isnot(None)).options(
            selectinload(Favorite.artist),
        )
    elif type == "playlist":
        query = query.where(Favorite.playlist_id.isnot(None)).options(
            selectinload(Favorite.playlist).selectinload(Playlist.owner),
        )

    from sqlalchemy import func
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Favorite.created_at.desc()).offset(offset).limit(page_size)
    )
    favorites = result.scalars().all()

    return PaginatedResponse(
        items=favorites,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/songs", response_model=List[SongWithRelations])
async def get_favorite_songs(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .options(
            selectinload(Favorite.song).selectinload(Song.artist),
            selectinload(Favorite.song).selectinload(Song.album),
        )
        .where(Favorite.user_id == current_user.id, Favorite.song_id.isnot(None))
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    return [SongWithRelations.model_validate(f.song, from_attributes=True) for f in favorites]


@router.get("/albums", response_model=List[AlbumResponse])
async def get_favorite_albums(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.album).selectinload(Album.artist))
        .where(Favorite.user_id == current_user.id, Favorite.album_id.isnot(None))
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    return [f.album for f in favorites]


@router.get("/artists", response_model=List[ArtistResponse])
async def get_favorite_artists(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.artist))
        .where(Favorite.user_id == current_user.id, Favorite.artist_id.isnot(None))
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    return [f.artist for f in favorites]


@router.get("/playlists", response_model=List[PlaylistResponse])
async def get_favorite_playlists(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.playlist).selectinload(Playlist.owner))
        .where(Favorite.user_id == current_user.id, Favorite.playlist_id.isnot(None))
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    return [f.playlist for f in favorites]


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    favorite_count = sum([
        favorite_data.song_id is not None,
        favorite_data.album_id is not None,
        favorite_data.artist_id is not None,
        favorite_data.playlist_id is not None,
    ])

    if favorite_count != 1:
        raise HTTPException(
            status_code=400,
            detail="Exactly one of song_id, album_id, artist_id, or playlist_id must be provided",
        )

    existing_query = select(Favorite).where(Favorite.user_id == current_user.id)
    if favorite_data.song_id:
        existing_query = existing_query.where(Favorite.song_id == favorite_data.song_id)
    elif favorite_data.album_id:
        existing_query = existing_query.where(Favorite.album_id == favorite_data.album_id)
    elif favorite_data.artist_id:
        existing_query = existing_query.where(Favorite.artist_id == favorite_data.artist_id)
    elif favorite_data.playlist_id:
        existing_query = existing_query.where(Favorite.playlist_id == favorite_data.playlist_id)

    existing = await db.execute(existing_query)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in favorites")

    favorite = Favorite(user_id=current_user.id, **favorite_data.model_dump())
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


@router.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_song(
    song_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.song_id == song_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    await db.delete(favorite)
    await db.commit()


@router.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_album(
    album_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.album_id == album_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    await db.delete(favorite)
    await db.commit()


@router.delete("/artists/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_artist(
    artist_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.artist_id == artist_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    await db.delete(favorite)
    await db.commit()


@router.delete("/playlists/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_playlist(
    playlist_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.playlist_id == playlist_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    await db.delete(favorite)
    await db.commit()


@router.get("/check/songs/{song_id}", response_model=bool)
async def check_favorite_song(
    song_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.song_id == song_id,
        )
    )
    return result.scalar_one_or_none() is not None