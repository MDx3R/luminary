import asyncio
import io
from collections.abc import Iterable, Sequence
from datetime import timedelta
from typing import BinaryIO

from common.application.exceptions import RepositoryError
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from minio import Minio, S3Error


class MinioFileStorage(IFileStorage):
    def __init__(self, client: Minio, bucket_name: str) -> None:
        self.client = client
        self.bucket_name = bucket_name

    async def upload(self, object_key: ObjectKey, mime: str, data: BinaryIO) -> None:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_key.value,
                    data=data,
                    length=-1,
                    content_type=mime,
                    part_size=8 * 1024 * 1024,
                ),
            )
        except S3Error as e:
            raise RepositoryError(f"Failed to upload file '{object_key}'") from e

    async def get_presigned_get_url(
        self, object_key: ObjectKey, expires_in: timedelta
    ) -> str:
        loop = asyncio.get_running_loop()
        try:
            url = await loop.run_in_executor(
                None,
                lambda: self.client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=object_key.value,
                    expires=expires_in,
                ),
            )
            return url
        except S3Error as e:
            # NOTE: Sice there is no exception for not found we can rely on S3 API to return 404 later on url use
            raise RepositoryError(
                f"Failed to generate presigned URL for '{object_key}'"
            ) from e

    async def get_presigned_get_urls(
        self, object_keys: Iterable[ObjectKey], expires_in: timedelta
    ) -> Sequence[str]:
        tasks = [self.get_presigned_get_url(key, expires_in) for key in object_keys]
        urls = await asyncio.gather(*tasks)
        return urls

    async def get(self, object_key: ObjectKey) -> BinaryIO:
        pass
        loop = asyncio.get_running_loop()

        def fetch() -> bytes:
            resp = self.client.get_object(
                bucket_name=self.bucket_name, object_name=object_key.value
            )
            try:
                return resp.read()
            finally:
                try:
                    resp.close()
                except Exception:
                    pass
                try:
                    resp.release_conn()
                except Exception:
                    pass

        try:
            data = await loop.run_in_executor(None, fetch)
            return io.BytesIO(data)
        except S3Error as e:
            raise RepositoryError(f"Failed to get file '{object_key}'") from e
