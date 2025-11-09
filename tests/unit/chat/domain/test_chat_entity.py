from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from tests.unit.chat.utils import make_chat_settings

from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings


class TestChatInfo:
    def test_create_success(self):
        info = ChatInfo(name="Test Chat")
        assert info.name == "Test Chat"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_invalid_name_raises(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            ChatInfo(name=name)


class TestChatSettings:
    def test_init_success(self):
        model_id = uuid4()
        max_context_messages = 10
        system_prompt = "Test prompt"

        settings = ChatSettings(
            model_id=model_id,
            system_prompt=system_prompt,
            max_context_messages=max_context_messages,
        )

        assert settings.model_id == model_id
        assert settings.system_prompt == system_prompt
        assert settings.max_context_messages == max_context_messages

    @pytest.mark.parametrize("prompt", ["", "   "])
    def test_empty_prompt_raises(self, prompt: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            make_chat_settings(system_prompt=prompt)

    @pytest.mark.parametrize("count", [-1, 0])
    def test_invalid_context_raises(self, count: Literal[-1] | Literal[0]):
        with pytest.raises(InvariantViolationError):
            make_chat_settings(max_context_messages=count)


class TestChat:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.chat_id = uuid4()
        self.user_id = uuid4()
        self.folder_id = uuid4()
        self.name = "Name"
        self.settings = make_chat_settings()
        self.created_at = DateTime(datetime.now(UTC))

        self.chat = Chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
            folder_id=self.folder_id,
            created_at=self.created_at,
            info=ChatInfo(name=self.name),
            settings=self.settings,
        )

    def test_create_chat_success(self):
        chat = Chat.create(
            chat_id=self.chat_id,
            user_id=self.user_id,
            folder_id=self.folder_id,
            name=self.name,
            settings=self.settings,
            created_at=self.created_at,
        )

        assert chat == self.chat

    def test_add_source_success(self):
        source_id = uuid4()
        self.chat.add_source(source_id)
        assert source_id in self.chat.sources

    def test_change_chat_name_success(self):
        self.chat.change_name("New Name")
        assert self.chat.info.name == "New Name"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_change_chat_name_invalid(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            self.chat.change_name(name)

    def test_change_settings_success(self):
        new_settings = make_chat_settings(
            system_prompt="New prompt", max_context_messages=15
        )
        self.chat.change_settings(new_settings)
        assert self.chat.settings == new_settings

    def test_with_none_folder_id(self):
        chat = Chat(
            chat_id=uuid4(),
            user_id=uuid4(),
            folder_id=None,
            created_at=DateTime(datetime.now(UTC)),
            info=ChatInfo(name="Test Chat"),
            settings=make_chat_settings(),
        )
        assert chat.folder_id is None
