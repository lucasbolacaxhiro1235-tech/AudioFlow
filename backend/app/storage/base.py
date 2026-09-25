import io
from typing import BinaryIO, Optional


class StorageBackend:
    name: str = "base"

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        raise NotImplementedError

    def upload_bytes(self, data: bytes, key: str, content_type: Optional[str] = None) -> bool:
        return self.upload_fileobj(io.BytesIO(data), key, content_type)

    def download_bytes(self, key: str) -> Optional[bytes]:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        raise NotImplementedError

    def presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        return self.public_url(key)

    def public_url(self, key: str) -> str:
        raise NotImplementedError