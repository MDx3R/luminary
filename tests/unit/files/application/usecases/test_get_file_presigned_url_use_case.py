from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from luminary_files.application.usecases.query.get_presigned_url_use_case import (
    GetFilePresignedUrlUseCase,
)
from luminary_files.domain.entity.file import File, FileId


@pytest.mark.asyncio
class TestGetFilePresignedUrlUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.object_key = str(uuid4())
        self.url = f"my-cloud/files/{self.object_key}"

        self.file = Mock(
            spec=File,
            id=FileId(uuid4()),
            object_key=ObjectKey(self.object_key),
            is_owned_by=Mock(return_value=True),
        )
        self.file_repository = AsyncMock(
            spec=IFileRepository, get_by_object_key=AsyncMock(return_value=self.file)
        )
        self.file_storage = AsyncMock(
            spec=IFileStorage,
            get_presigned_get_url=AsyncMock(return_value=self.url),
        )

        self.use_case = GetFilePresignedUrlUseCase(
            self.file_repository, self.file_storage
        )

        self.query = GetPresignedUrlQuery(
            user_id=self.user_id, object_key=self.object_key
        )

    async def test_execute_success(self):
        # Act
        result = await self.use_case.execute(self.query)

        # Assert
        assert result == self.url

        self.file_repository.get_by_object_key.assert_awaited_once_with(
            ObjectKey(self.object_key)
        )
        self.file_storage.get_presigned_get_url.assert_awaited_once_with(
            ObjectKey(self.object_key), self.use_case.EXPIRATION_DELTA
        )

    async def test_execute_no_access_raises(self):
        # Arrange
        self.file.is_owned_by = Mock(return_value=False)

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.query)
