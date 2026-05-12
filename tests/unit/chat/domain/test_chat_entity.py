from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.events.events import (
    ChatCreatedEvent,
    ChatNameChangedEvent,
    ChatSourceAddedEvent,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class TestChatInfo:
    def test_create_success(self):
        info = ChatInfo(name="Test Chat")
        assert info.name == "Test Chat"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_invalid_name_raises(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            ChatInfo(name=name)


class TestChat:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.chat_id = ChatId(uuid4())
        self.user_id = UserId(uuid4())
        self.folder_id = FolderId(uuid4())
        self.assistant_id = AssistantId(uuid4())
        self.name = "Name"
        self.created_at = DateTime(datetime.now(UTC))

        self.chat = Chat(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=self.assistant_id,
            created_at=self.created_at,
            info=ChatInfo(name=self.name),
            is_deleted=False,
        )

    def test_create_chat_success(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=self.assistant_id,
            name=self.name,
            created_at=self.created_at,
        )

        assert chat == self.chat

    def test_create_chat_emits_created_event(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=self.assistant_id,
            name=self.name,
            created_at=self.created_at,
        )

        assert chat.has_changes()
        assert len(chat.events) == 1
        event = chat.events[0]
        assert isinstance(event, ChatCreatedEvent)
        assert event.chat_id == self.chat_id.value
        assert event.owner_id == self.user_id.value
        assert event.folder_id == self.folder_id.value
        assert event.name == self.name
        assert event.assistant_id == self.assistant_id.value
        assert event.created_at == self.created_at.value

    def test_add_source_success(self):
        source_id = SourceId(uuid4())
        self.chat.add_source(source_id)
        assert source_id in self.chat.sources

    def test_add_source_emits_event_and_idempotent(self):
        source_id = SourceId(uuid4())
        self.chat.add_source(source_id)
        assert len(self.chat.events) == 1
        assert isinstance(self.chat.events[0], ChatSourceAddedEvent)
        self.chat.add_source(source_id)
        assert len(self.chat.events) == 1

    def test_change_chat_name_success(self):
        self.chat.change_name("New Name")
        assert self.chat.info.name == "New Name"
        assert len(self.chat.events) == 1
        assert isinstance(self.chat.events[0], ChatNameChangedEvent)
        assert self.chat.events[0].name == "New Name"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_change_chat_name_invalid(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            self.chat.change_name(name)

    def test_with_none_folder_id(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=None,
            assistant_id=self.assistant_id,
            created_at=DateTime(datetime.now(UTC)),
            name="Test Chat",
        )
        assert chat.folder_id is None

    def test_with_none_assistant_id(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=None,
            created_at=DateTime(datetime.now(UTC)),
            name="Test Chat",
        )
        assert chat.assistant_id is None
