from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.domain.entity.file import File, FileId
from luminary_files.domain.exceptions import InvalidMIMETypeError
from luminary_files.domain.factories.file_factory import FileFactory
from luminary_files.domain.interfaces.extenstion_policy import IMIMEPolicy
from luminary_files.domain.value_objects.file_meta import FileMeta
from tests.unit.utils import MockClock, MockUUIDGenerator


class TestPhotoFactory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file_id = uuid4()
        self.user_id = uuid4()
        self.now = DateTime(datetime.now(UTC))
        self.mime = "text/plain"
        self.bucket = "files"

        self.clock = MockClock(self.now)
        self.uuid_generator = MockUUIDGenerator(self.file_id)

        self.ext_policy = Mock(spec=IMIMEPolicy, is_allowed=Mock(return_value=True))

        self.factory = FileFactory(self.clock, self.uuid_generator, self.ext_policy)

    def test_create_success(self):
        # Arrange
        filename = "file.txt"

        # Act
        result = self.factory.create(
            user_id=UserId(self.user_id),
            filename=filename,
            bucket=self.bucket,
            mime=self.mime,
        )

        # Assert
        assert result == File(
            id=FileId(self.file_id),
            owner_id=UserId(self.user_id),
            meta=FileMeta(filename=filename, mime_type=self.mime, filesize=None),
            bucket=self.bucket,
            object_key=ObjectKey(str(self.file_id)),
            uploaded_at=self.now,
        )

        self.ext_policy.is_allowed.assert_called_once_with(self.mime)

    def test_create_invalid_extension_fails(self):
        # Arrange
        filename = "file.txt"
        self.ext_policy.is_allowed.return_value = False

        # Act
        with pytest.raises(InvalidMIMETypeError):
            self.factory.create(
                user_id=UserId(self.user_id),
                filename=filename,
                bucket=self.bucket,
                mime=self.mime,
            )

        # Assert
        self.ext_policy.is_allowed.assert_called_once_with(self.mime)
