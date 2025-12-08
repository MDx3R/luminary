from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo
from luminary.source.domain.entity.source import SourceId


class TestFolderInfo:
    def test_create_success(self):
        info = FolderInfo(name="Folder Info", description="Folder Description")
        assert info.name == "Folder Info"
        assert info.description == "Folder Description"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_invalid_name_raises(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            FolderInfo(name=name, description="Folder Description")


class TestFolder:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.folder_id = FolderId(uuid4())
        self.owner_id = UserId(uuid4())

        self.name = "Folder Name"
        self.description = "Folder Description"

        self.assistant_id = AssistantId(uuid4())
        self.created_at = DateTime(datetime.now(UTC))

        self.folder = Folder(
            id=self.folder_id,
            owner_id=self.owner_id,
            info=FolderInfo(name=self.name, description=self.description),
            assistant_id=self.assistant_id,
            created_at=self.created_at,
        )

    def test_create_folder_success(self):
        folder = Folder.create(
            id=self.folder_id,
            owner_id=self.owner_id,
            name=self.name,
            description=self.description,
            assistant_id=self.assistant_id,
            created_at=self.created_at,
        )

        assert folder == self.folder

    def test_change_name_success(self):
        new_name = "Updated Name"
        self.folder.change_name(new_name)
        assert self.folder.info.name == new_name

    @pytest.mark.parametrize("name", ["", "   "])
    def test_change_name_invalid(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            self.folder.change_name(name)

    def test_change_description_success(self):
        new_description = "Updated Description"
        self.folder.change_description(new_description)
        assert self.folder.info.description == new_description

    def test_add_and_remove_chat(self):
        chat_id = ChatId(uuid4())

        self.folder.add_chat(chat_id)
        assert self.folder.has_chat(chat_id)

        self.folder.remove_chat(chat_id)
        assert not self.folder.has_chat(chat_id)

    def test_add_and_remove_source(self):
        source_id = SourceId(uuid4())

        self.folder.add_source(source_id)
        assert self.folder.has_source(source_id)

        self.folder.remove_source(source_id)
        assert not self.folder.has_source(source_id)

    def test_change_assistant(self):
        new_assistant_id = AssistantId(uuid4())
        self.folder.change_assistant(new_assistant_id)
        assert self.folder.assistant_id == new_assistant_id

    def test_with_none_assistant_id(self):
        folder = Folder.create(
            id=self.folder_id,
            owner_id=self.owner_id,
            name=self.name,
            description=self.description,
            assistant_id=None,
            created_at=self.created_at,
        )
        assert folder.assistant_id is None
