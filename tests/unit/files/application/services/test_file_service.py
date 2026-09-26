from datetime import timedelta
from io import BytesIO
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.application.dtos.dtos import FileType
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from luminary_files.application.interfaces.services.file_service import (
    UploadFileCommand,
)
from luminary_files.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)
from luminary_files.application.services.file_service import FileService
from luminary_files.domain.entity.file import File, FileId
from luminary_files.domain.interfaces.file_factory import IFileFactory
from luminary_files.domain.value_objects.file_meta import FileMeta


@pytest.mark.asyncio
class TestFileService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.file_id = uuid4()
        self.filename = "test.txt"
        self.content = BytesIO(b"test data")
        self.mime = "text/plain"
        self.bucket = "files"
        self.object_key_value = "some/object/key"
        self.object_key = ObjectKey(self.object_key_value)
        self.size = len(b"test data")
        self.expiration_delta = timedelta(days=7)
        self.presigned_url = "https://presigned.url"

        self.file_type = FileType(mime=self.mime, extension="txt")
        self.file = Mock(
            spec=File,
            id=FileId(self.file_id),
            meta=FileMeta(self.filename, self.mime, None),
            object_key=self.object_key,
            specify_size=Mock(),
        )

        self.file_factory = Mock(spec=IFileFactory, create=Mock(return_value=self.file))

        self.file_type_introspector = Mock(
            spec=IFileTypeIntrospector, extract=Mock(return_value=self.file_type)
        )
        self.file_repository = AsyncMock(spec=IFileRepository)
        self.file_storage = AsyncMock(
            spec=IFileStorage,
            get_presigned_get_url=AsyncMock(return_value=self.presigned_url),
        )

        self.service = FileService(
            self.bucket,
            self.file_factory,
            self.file_type_introspector,
            self.file_repository,
            self.file_storage,
        )

    async def test_upload_file_success(self) -> None:
        # Arrange
        command = UploadFileCommand(
            user_id=self.user_id,
            filename=self.filename,
            content=self.content,
        )

        # Act
        result = await self.service.upload_file(command)

        # Assert
        assert result == self.file_id

        self.file_type_introspector.extract.assert_called_once_with(self.content)
        self.file_factory.create.assert_called_once_with(
            user_id=UserId(self.user_id),
            filename=self.filename,
            bucket=self.bucket,
            mime=self.mime,
        )
        self.file_storage.upload.assert_awaited_once_with(
            self.object_key,
            self.mime,
            self.content,
        )
        self.file.specify_size.assert_called_once_with(self.size)
        self.file_repository.add.assert_awaited_once_with(self.file)

        # Verify seek calls
        assert (
            self.content.tell() == 0
        )  # Should be reset to start after size extraction

    async def test_upload_file_with_empty_content(self) -> None:
        # NOTE: Actually, file type introspector should raise if content is empty/invalid

        # Arrange
        empty_content = BytesIO(b"")
        command = UploadFileCommand(
            user_id=self.user_id,
            filename=self.filename,
            content=empty_content,
        )
        self.file.specify_size.reset_mock()

        # Act
        result = await self.service.upload_file(command)

        # Assert
        assert result == self.file_id
        self.file.specify_size.assert_called_once_with(0)
        assert empty_content.tell() == 0
