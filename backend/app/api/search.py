from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_user
from app.models import Song, Artist, Album, Playlist, Favorite
from app.schemas import (
    SearchResult, SongWithRelations, ArtistResponse, AlbumResponse, PlaylistResponse
)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(10, ge=1, le=50),
    current_user_id: Optional[UUID] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    search_term = f"%{q}%"

    tracks_result = await db.execute(
        select(Song)
        .options(selectinload(Song.artist), selectinload(Song.album))
        .where(
            or_(
                Song.title.ilike(search_term),
                Song.spotify_id.ilike(search_term),
            )
        )
        .limit(limit)
    )
    tracks = tracks_result.scalars().all()

    artists_result = await db.execute(
        select(Artist)
        .where(Artist.name.ilike(search_term))
        .limit(limit)
    )
    artists = artists_result.scalars().all()

    albums_result = await db.execute(
        select(Album)
        .options(selectinload(Album.artist))
        .where(
            or_(
                Album.title.ilike(search_term),
                Album.spotify_id.ilike(search_term),
            )
        )
        .limit(limit)
    )
    albums = albums_result.scalars().all()

    playlists_result = await db.execute(
        select(Playlist)
        .where(Playlist.name.ilike(search_term))
        .limit(limit)
    )
    playlists = playlists_result.scalars().all()

    favorite_track_ids = set()
    if current_user_id:
        fav_result = await db.execute(
            select(Favorite.song_id).where(
                Favorite.user_id == current_user_id,
                Favorite.song_id.isnot(None),
            )
        )
        favorite_track_ids = {row[0] for row in fav_result.all()}

    track_responses = []
    for track in tracks:
        tr = SongWithRelations.model_validate(track)
        tr.is_favorite = track.id in favorite_track_ids
        track_responses.append(tr)

    return SearchResult(
        tracks=track_responses,
        artists=artists,
        albums=albums,
        playlists=playlists,
    )


@router.get("/suggestions", response_model=List[str])
async def search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
):
    search_term = f"%{q}%"

    suggestions = []

    track_titles = await db.execute(
        select(Song.title).where(Song.title.ilike(search_term)).limit(limit)
    )
    suggestions.extend([row[0] for row in track_titles.all()])

    artist_names = await db.execute(
        select(Artist.name).where(Artist.name.ilike(search_term)).limit(limit)
    )
    suggestions.extend([row[0] for row in artist_names.all()])

    album_titles = await db.execute(
        select(Album.title).where(Album.title.ilike(search_term)).limit(limit)
    )
    suggestions.extend([row[0] for row in album_titles.all()])

    return suggestions[:limit]