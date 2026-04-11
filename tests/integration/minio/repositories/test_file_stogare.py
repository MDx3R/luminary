from datetime import timedelta
from http import HTTPStatus
from io import BytesIO
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.infrastructure.storage.minio.repositories.file_storage import (
    MinioFileStorage,
)
from minio import Minio


@pytest.mark.asyncio
class TestMinioFileStorage:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, minio: Minio):
        self.bucket_name = "test-bucket"
        self.client = minio
        self.repository = MinioFileStorage(self.client, self.bucket_name)

        if not minio.bucket_exists(self.bucket_name):
            minio.make_bucket(self.bucket_name)
        async with httpx.AsyncClient() as http_client:
            self.http_client = http_client
            yield
        # Clean up
        objects = self.client.list_objects(self.bucket_name, recursive=True)
        for obj in objects:
            if not obj.object_name:
                continue
            self.client.remove_object(self.bucket_name, obj.object_name)

    def _get_object_key(self) -> ObjectKey:
        return ObjectKey(str(uuid4()))

    def _get_file_data(self) -> BytesIO:
        return BytesIO(b"fake_file_data")

    async def _add_file(self, object_key: ObjectKey, mime: str) -> None:
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_key.value,
            data=self._get_file_data(),
            length=self._get_file_data().getbuffer().nbytes,
            content_type=mime,
        )

    async def test_upload_photo_success(self):
        # Arrange
        object_key = self._get_object_key()
        mime = "text/plain"
        data = self._get_file_data()

        # Act
        await self.repository.upload(object_key, mime, data)

        # Assert
        objects = list(self.client.list_objects(self.bucket_name))

        assert len(objects) == 1
        assert objects[0].object_name == object_key.value

        stat = self.client.stat_object(self.bucket_name, object_key.value)
        assert stat.content_type == mime

    async def test_get_presigned_get_url_success(self):
        # Arrange
        object_key = self._get_object_key()
        mime = "text/plain"
        expires_in = timedelta(minutes=5)

        await self._add_file(object_key, mime)

        # Act
        url = await self.repository.get_presigned_get_url(object_key, expires_in)

        # Assert
        assert isinstance(url, str)
        assert f"{self.bucket_name}/{object_key.value}" in url

        # Assert response
        response = await self.http_client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == mime
        assert response.content == self._get_file_data().getbuffer()

    async def test_get_presigned_get_urls_success(self):
        # Arrange
        object_keys = [self._get_object_key() for _ in range(2)]
        mime = "text/plain"
        expires_in = timedelta(minutes=5)
        for key in object_keys:
            await self._add_file(key, mime)

        # Act
        urls = await self.repository.get_presigned_get_urls(object_keys, expires_in)

        # Assert
        assert len(urls) == len(object_keys)
        for url, name in zip(urls, object_keys, strict=True):
            assert isinstance(url, str)
            assert f"{self.bucket_name}/{name.value}" in url

            # Assert response
            response = await self.http_client.get(url)
            assert response.status_code == HTTPStatus.OK
            assert response.headers["Content-Type"] == mime
            assert response.content == self._get_file_data().getbuffer()

    async def test_get_success(self):
        # Arrange
        object_key = self._get_object_key()
        mime = "text/plain"

        await self._add_file(object_key, mime)

        # Act
        result = await self.repository.get(object_key)

        # Assert
        content = result.read()
        assert content == self._get_file_data().getbuffer()
