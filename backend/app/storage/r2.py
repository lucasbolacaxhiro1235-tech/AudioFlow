import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from uuid import uuid4
import mimetypes
from app.config import settings


class R2Storage:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            region_name="auto",
        )
        self.bucket = settings.R2_BUCKET
        self.public_url = settings.R2_PUBLIC_URL

    def _get_content_type(self, filename: str) -> str:
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_fileobj(file, self.bucket, key, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            print(f"R2 upload error: {e}")
            return False

    def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra_args)
            return True
        except ClientError as e:
            print(f"R2 upload bytes error: {e}")
            return False

    def download_file(self, key: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            print(f"R2 download error: {e}")
            return None

    def delete_file(self, key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            print(f"R2 delete error: {e}")
            return False

    def generate_presigned_url(
        self, key: str, expiration: int = 3600, method: str = "get_object"
    ) -> Optional[str]:
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=method,
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            print(f"R2 presigned URL error: {e}")
            return None

    def get_public_url(self, key: str) -> str:
        return f"{self.public_url}/{key}"

    def file_exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_file_size(self, key: str) -> Optional[int]:
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=key)
            return response.get("ContentLength")
        except ClientError:
            return None

    def generate_audio_key(self, user_id: str, filename: str) -> str:
        ext = filename.split(".")[-1] if "." in filename else "mp3"
        return f"songs/{user_id}/{uuid4()}.{ext}"

    def generate_cover_key(self, user_id: str, filename: str) -> str:
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        return f"covers/{user_id}/{uuid4()}.{ext}"

    def generate_temp_key(self, user_id: str, filename: str) -> str:
        ext = filename.split(".")[-1] if "." in filename else "tmp"
        return f"temporary/{user_id}/{uuid4()}.{ext}"


r2_storage = R2Storage()