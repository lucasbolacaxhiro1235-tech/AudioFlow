from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj
from app.models import User, Playlist, Song, Favorite, History
from app.schemas import UserResponse, PlaylistResponse, SongWithRelations, HistoryResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/playlists", response_model=PaginatedResponse)
async def get_my_playlists(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(Playlist.id)).where(Playlist.owner_id == current_user.id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Playlist)
        .where(Playlist.owner_id == current_user.id)
        .order_by(Playlist.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    playlists = result.scalars().all()

    return PaginatedResponse(
        items=playlists,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/me/favorites", response_model=PaginatedResponse)
async def get_my_favorites(
    type: Optional[str] = Query(None, regex="^(song|album|artist|playlist)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(Favorite).where(Favorite.user_id == current_user.id)

    if type == "song":
        query = query.where(Favorite.song_id.isnot(None))
    elif type == "album":
        query = query.where(Favorite.album_id.isnot(None))
    elif type == "artist":
        query = query.where(Favorite.artist_id.isnot(None))
    elif type == "playlist":
        query = query.where(Favorite.playlist_id.isnot(None))

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


@router.get("/me/history", response_model=PaginatedResponse)
async def get_my_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count(History.id)).where(History.user_id == current_user.id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(History)
        .where(History.user_id == current_user.id)
        .order_by(History.played_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    history = result.scalars().all()

    return PaginatedResponse(
        items=history,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.delete("/me/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_history(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        select(History).where(History.user_id == current_user.id).delete()
    )
    await db.commit()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user