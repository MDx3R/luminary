from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings


class TestChatEntity:
    def test_create_chat_success(self) -> None:
        """Проверяем успешное создание чата."""
        chat_id: UUID = uuid4()
        user_id: UUID = uuid4()
        model_id: UUID = uuid4()
        folder_id: UUID = uuid4()
        name: str = "My Chat"
        system_prompt: str = "You are helpful"
        max_context_messages: int = 10
        created_at: DateTime = DateTime(datetime.now(UTC))

        chat_info: ChatInfo = ChatInfo(name=name)
        chat_settings: ChatSettings = ChatSettings(
            model_id=model_id,
            system_prompt=system_prompt,
            max_context_messages=max_context_messages,
        )

        chat: Chat = Chat(
            chat_id=chat_id,
            user_id=user_id,
            folder_id=folder_id,
            created_at=created_at,
            info=chat_info,
            settings=chat_settings,
        )

        assert chat.chat_id == chat_id
        assert chat.user_id == user_id
        assert chat.folder_id == folder_id
        assert chat.created_at == created_at
        assert chat.info.name == name
        assert chat.settings.model_id == model_id
        assert chat.settings.system_prompt == system_prompt
        assert chat.settings.max_context_messages == max_context_messages

    def test_chat_info_empty_name_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError) as exc_info:
            ChatInfo(name="")
        assert "Chat name cannot be empty" in str(exc_info.value)

    def test_chat_info_whitespace_name_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError) as exc_info:
            ChatInfo(name="   ")
        assert "Chat name cannot be empty" in str(exc_info.value)

    def test_chat_settings_empty_prompt_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError) as exc_info:
            ChatSettings(
                model_id=uuid4(),
                system_prompt="",
                max_context_messages=10,
            )
        assert "System prompt cannot be empty" in str(exc_info.value)

    def test_chat_settings_negative_context_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError) as exc_info:
            ChatSettings(
                model_id=uuid4(),
                system_prompt="Prompt",
                max_context_messages=-1,
            )
        assert "Number of context messages cannot be non-positive" in str(
            exc_info.value
        )

    def test_chat_settings_zero_context_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError) as exc_info:
            ChatSettings(
                model_id=uuid4(),
                system_prompt="Prompt",
                max_context_messages=0,
            )
        assert "Number of context messages cannot be non-positive" in str(
            exc_info.value
        )

    def test_change_chat_name_success(self) -> None:
        chat: Chat = self._create_chat(name="Old Name")
        new_name: str = "New Name"

        chat.change_name(new_name)

        assert chat.info.name == new_name

    def test_change_chat_settings_success(self) -> None:
        chat: Chat = self._create_chat()
        new_settings: ChatSettings = ChatSettings(
            model_id=uuid4(),
            system_prompt="New prompt",
            max_context_messages=15,
        )

        chat.change_settings(new_settings)

        assert chat.settings.model_id == new_settings.model_id
        assert chat.settings.system_prompt == new_settings.system_prompt
        assert chat.settings.max_context_messages == new_settings.max_context_messages

    def test_chat_with_none_folder_id_success(self) -> None:
        chat_id: UUID = uuid4()
        user_id: UUID = uuid4()
        model_id: UUID = uuid4()
        created_at: DateTime = DateTime(datetime.now(UTC))

        chat_info: ChatInfo = ChatInfo(name="Test Chat")
        chat_settings: ChatSettings = ChatSettings(
            model_id=model_id,
            system_prompt="Test prompt",
            max_context_messages=10,
        )

        chat: Chat = Chat(
            chat_id=chat_id,
            user_id=user_id,
            folder_id=None,
            created_at=created_at,
            info=chat_info,
            settings=chat_settings,
        )

        assert chat.chat_id == chat_id
        assert chat.user_id == user_id
        assert chat.folder_id is None
        assert chat.created_at == created_at

    def test_change_chat_name_empty_raises_error(self) -> None:
        chat: Chat = self._create_chat(name="Old Name")

        with pytest.raises(InvariantViolationError) as exc_info:
            chat.change_name("")
        assert "Chat name cannot be empty" in str(exc_info.value)

    def test_change_chat_name_whitespace_raises_error(self) -> None:
        chat: Chat = self._create_chat(name="Old Name")

        with pytest.raises(InvariantViolationError) as exc_info:
            chat.change_name("   ")
        assert "Chat name cannot be empty" in str(exc_info.value)

    def test_change_chat_settings_empty_prompt_raises_error(self) -> None:
        self._create_chat()

        with pytest.raises(InvariantViolationError) as exc_info:
            ChatSettings(
                model_id=uuid4(),
                system_prompt="",
                max_context_messages=15,
            )
        assert "System prompt cannot be empty" in str(exc_info.value)

    def test_change_chat_settings_invalid_context_raises_error(self) -> None:
        self._create_chat()

        with pytest.raises(InvariantViolationError) as exc_info:
            ChatSettings(
                model_id=uuid4(),
                system_prompt="Valid prompt",
                max_context_messages=0,
            )
        assert "Number of context messages cannot be non-positive" in str(
            exc_info.value
        )

    def test_change_chat_settings_with_valid_settings_success(self) -> None:
        chat: Chat = self._create_chat()
        valid_settings: ChatSettings = ChatSettings(
            model_id=uuid4(),
            system_prompt="Valid prompt",
            max_context_messages=15,
        )

        chat.change_settings(valid_settings)

        assert chat.settings == valid_settings

    def _create_chat(  # noqa: PLR0913
        self,
        chat_id: UUID | None = None,
        user_id: UUID | None = None,
        name: str = "Test Chat",
        system_prompt: str = "Test prompt",
        max_context_messages: int = 10,
        model_id: UUID | None = None,
        folder_id: UUID | None = None,
    ) -> Chat:
        final_chat_id: UUID = chat_id or uuid4()
        final_user_id: UUID = user_id or uuid4()
        final_model_id: UUID = model_id or uuid4()
        final_folder_id: UUID = folder_id or uuid4()

        chat_info: ChatInfo = ChatInfo(name=name)
        chat_settings: ChatSettings = ChatSettings(
            model_id=final_model_id,
            system_prompt=system_prompt,
            max_context_messages=max_context_messages,
        )

        return Chat(
            chat_id=final_chat_id,
            user_id=final_user_id,
            folder_id=final_folder_id,
            created_at=DateTime(datetime.now(UTC)),
            info=chat_info,
            settings=chat_settings,
        )
