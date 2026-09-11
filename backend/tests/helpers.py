import uuid

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Download, DownloadStatus, File, StorageBackend, AudioMetadata


async def insert_file(user_id, title="Faixa Teste", artist="Artista Teste"):
    async with AsyncSessionLocal() as db:
        f = File(
            user_id=uuid.UUID(str(user_id)),
            storage=StorageBackend.LOCAL,
            object_key=f"songs/{user_id}/{uuid.uuid4()}.mp3",
            file_name="test.mp3",
            mime_type="audio/mpeg",
            format="mp3",
            size_bytes=12345,
        )
        db.add(f)
        await db.flush()
        m = AudioMetadata(file_id=f.id, title=title, artist=artist, duration_seconds=180.0)
        db.add(m)
        await db.commit()
        await db.refresh(f)
        return f.id


async def insert_download(user_id, url="https://example.com/track", status=DownloadStatus.PENDING):
    async with AsyncSessionLocal() as db:
        d = Download(
            user_id=uuid.UUID(str(user_id)), url=url, kind="track", format="mp3", quality="192k",
            status=status, stage="queued",
        )
        db.add(d)
        await db.commit()
        await db.refresh(d)
        return d.id


async def get_user_id(header_name, value):
    from app.database import AsyncSessionLocal
    from app.models import User

    async with AsyncSessionLocal() as db:
        u = (await db.execute(select(User).where(User.email == value))).scalar_one_or_none()
        return u.id if u else None