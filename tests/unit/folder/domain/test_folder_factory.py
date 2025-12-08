from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from tests.unit.utils import MockClock, MockUUIDGenerator

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.factories.folder_factory import FolderFactory
from luminary.folder.domain.value_objects.folder_id import FolderId


class TestFolderFactory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.name = "Folder Name"
        self.description = "Folder Description"
        self.folder_id = FolderId(uuid4())
        self.owner_id = UserId(uuid4())
        self.assistant_id = AssistantId(uuid4())
        self.created_at = DateTime(datetime.now(UTC))

        self.factory = FolderFactory(
            clock=MockClock(self.created_at),
            uuid_generator=MockUUIDGenerator(self.folder_id.value),
        )

    def test_create_folder_success(self):
        folder = self.factory.create(
            name=self.name,
            description=self.description,
            user_id=self.owner_id,
            assistant_id=self.assistant_id,
        )

        assert isinstance(folder, Folder)
        assert folder.info.name == self.name
        assert folder.info.description == self.description
        assert folder.owner_id == self.owner_id
        assert folder.assistant_id == self.assistant_id

    def test_create_folder_with_none_description(self):
        folder = self.factory.create(
            name=self.name,
            description=None,
            user_id=self.owner_id,
            assistant_id=self.assistant_id,
        )

        assert folder.info.description is None
