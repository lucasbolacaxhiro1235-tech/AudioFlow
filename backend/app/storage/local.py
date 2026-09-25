import os
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4

from app.config import settings
from .base import StorageBackend


class LocalStorage(StorageBackend):
    name = "local"

    def __init__(self):
        self.root = Path(settings.STORAGE_LOCAL_PATH).resolve()

    def _safe(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not str(path).startswith(str(self.root)):
            raise ValueError("Invalid storage key")
        return path

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        try:
            path = self._safe(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as out:
                while True:
                    chunk = fileobj.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            return True
        except Exception:
            return False

    def download_bytes(self, key: str) -> Optional[bytes]:
        path = self._safe(key)
        if not path.exists():
            return None
        return path.read_bytes()

    def delete(self, key: str) -> bool:
        try:
            path = self._safe(key)
            if path.exists():
                os.remove(path)
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        return self._safe(key).exists()

    def public_url(self, key: str) -> str:
        return f"{settings.STORAGE_PUBLIC_BASE_URL.rstrip('/')}/{key}"

    def generate_key(self, category: str, user_id: str, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        return f"{category}/{user_id}/{uuid4()}.{ext}"


local_storage = LocalStorage()