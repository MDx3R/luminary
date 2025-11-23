from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.services.file_service import IFileService
from luminary_files.application.usecases.query.get_presigned_url_use_case import (
    GetFilePresignedUrlUseCase,
)


@pytest.mark.asyncio
class TestGetFilePresignedUrlUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.object_key = str(uuid4())
        self.url = f"my-cloud/files/{self.object_key}"

        self.file_service = AsyncMock(spec=IFileService)
        self.file_service.get_file_presigned_url.return_value = self.url

        self.use_case = GetFilePresignedUrlUseCase(self.file_service)

        self.query = GetPresignedUrlQuery(self.object_key)

    async def test_execute_success(self):
        # Act
        result = await self.use_case.execute(self.query)

        # Assert
        assert result == self.url

        self.file_service.get_file_presigned_url.assert_awaited_once_with(self.query)
