import mimetypes
from typing import BinaryIO, Optional
from uuid import uuid4

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import settings
from .base import StorageBackend


class S3Storage(StorageBackend):
    name = "s3"

    def __init__(self):
        endpoint = settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None
        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
            "region_name": settings.S3_REGION or "auto",
        }
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        self.client = boto3.client(
            **kwargs,
            config=BotoConfig(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET
        self.public_base = settings.S3_PUBLIC_URL

    def _content_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or "application/octet-stream"

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        try:
            extra = {"ContentType": content_type or self._content_type(key)}
            if metadata:
                extra["Metadata"] = metadata
            self.client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra)
            return True
        except ClientError:
            return False

    def download_bytes(self, key: str) -> Optional[bytes]:
        try:
            resp = self.client.get_object(Bucket=self.bucket, Key=key)
            return resp["Body"].read()
        except ClientError:
            return None

    def delete(self, key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expiration,
            )
        except ClientError:
            return None

    def public_url(self, key: str) -> str:
        if self.public_base:
            return f"{self.public_base.rstrip('/')}/{key}"
        return self.presigned_url(key) or f"s3://{self.bucket}/{key}"

    def generate_key(self, category: str, user_id: str, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        return f"{category}/{user_id}/{uuid4()}.{ext}"


s3_storage = S3Storage()