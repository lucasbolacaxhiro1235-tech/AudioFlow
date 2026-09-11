from app.config import settings
from app.storage.base import StorageBackend


def get_storage() -> StorageBackend:
    backend = settings.STORAGE_BACKEND.lower()
    if backend in ("s3", "r2"):
        from app.storage.s3 import s3_storage

        return s3_storage
    from app.storage.local import local_storage

    return local_storage


storage = get_storage()