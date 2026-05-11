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
    ChatNameChangedEvent,
    ChatSettingsChangedEvent,
    ChatSourceAddedEvent,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.domain.entity.model import ModelId
from luminary.source.domain.entity.source import SourceId


class TestChatInfo:
    def test_create_success(self):
        info = ChatInfo(name="Test Chat")
        assert info.name == "Test Chat"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_invalid_name_raises(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            ChatInfo(name=name)


class TestChatMaxContext:
    @pytest.mark.parametrize("count", [-1, 0])
    def test_invalid_max_context_on_construct_raises(self, count: int):
        with pytest.raises(InvariantViolationError):
            Chat(
                id=ChatId(uuid4()),
                owner_id=UserId(uuid4()),
                folder_id=None,
                assistant_id=None,
                created_at=DateTime(datetime.now(UTC)),
                info=ChatInfo(name="x"),
                model_id=ModelId(uuid4()),
                max_context_messages=count,
                is_deleted=False,
            )


class TestChat:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.chat_id = ChatId(uuid4())
        self.user_id = UserId(uuid4())
        self.folder_id = FolderId(uuid4())
        self.assistant_id = AssistantId(uuid4())
        self.name = "Name"
        self.model_id = ModelId(uuid4())
        self.max_context_messages = 10
        self.created_at = DateTime(datetime.now(UTC))

        self.chat = Chat(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=self.assistant_id,
            created_at=self.created_at,
            info=ChatInfo(name=self.name),
            model_id=self.model_id,
            max_context_messages=self.max_context_messages,
            is_deleted=False,
        )

    def test_create_chat_success(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=self.folder_id,
            assistant_id=self.assistant_id,
            name=self.name,
            model_id=self.model_id,
            max_context_messages=self.max_context_messages,
            created_at=self.created_at,
        )

        assert chat == self.chat

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

    def test_update_model_and_context_success(self):
        new_model = ModelId(uuid4())
        self.chat.update_model_and_context(new_model, 15)
        assert self.chat.model_id == new_model
        assert self.chat.max_context_messages == 15  # noqa: PLR2004
        assert len(self.chat.events) == 1
        assert isinstance(self.chat.events[0], ChatSettingsChangedEvent)

    @pytest.mark.parametrize("count", [-1, 0])
    def test_update_model_and_context_invalid_raises(self, count: int):
        with pytest.raises(InvariantViolationError):
            self.chat.update_model_and_context(ModelId(uuid4()), count)

    def test_with_none_folder_id(self):
        chat = Chat.create(
            id=self.chat_id,
            owner_id=self.user_id,
            folder_id=None,
            assistant_id=self.assistant_id,
            created_at=DateTime(datetime.now(UTC)),
            name="Test Chat",
            model_id=ModelId(uuid4()),
            max_context_messages=10,
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
            model_id=ModelId(uuid4()),
            max_context_messages=10,
        )
        assert chat.assistant_id is None
