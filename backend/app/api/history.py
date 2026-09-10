from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user_obj
from app.models import History, Song
from app.schemas import HistoryCreate, HistoryResponse, SongWithRelations, PaginatedResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=PaginatedResponse)
async def get_history(
    page: int = 1,
    page_size: int = 50,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    query = select(History).where(History.user_id == current_user.id)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.options(
            selectinload(History.song).selectinload(Song.artist),
            selectinload(History.song).selectinload(Song.album),
        )
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


@router.get("/recent", response_model=List[SongWithRelations])
async def get_recent_history(
    limit: int = 20,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(History)
        .options(
            selectinload(History.song).selectinload(Song.artist),
            selectinload(History.song).selectinload(Song.album),
        )
        .where(History.user_id == current_user.id)
        .order_by(History.played_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    return [SongWithRelations.model_validate(h.song, from_attributes=True) for h in history]


@router.post("", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_to_history(
    history_data: HistoryCreate,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(History).where(
            History.user_id == current_user.id,
            History.song_id == history_data.song_id,
        ).order_by(History.played_at.desc())
    )
    existing_history = existing.scalar_one_or_none()

    if existing_history:
        existing_history.progress = history_data.progress
        existing_history.completed = history_data.completed
        existing_history.played_at = __import__("datetime").datetime.utcnow()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history

    history = History(user_id=current_user.id, **history_data.model_dump())
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(History).where(History.user_id == current_user.id)
    )
    await db.commit()


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_history(
    history_id: UUID,
    current_user = Depends(get_current_user_obj),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(History).where(
            History.id == history_id,
            History.user_id == current_user.id,
        )
    )
    history = result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")

    await db.delete(history)
    await db.commit()