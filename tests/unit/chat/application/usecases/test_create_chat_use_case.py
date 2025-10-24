from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
)
from luminary.chat.application.usecases.command.create_chat_use_case import (
    CreateChatUseCase,
)
from luminary.chat.domain.entity.chat import ChatSettings
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)


@dataclass(frozen=True)
class CreateChatFactoryParams:
    """DTO для параметров создания чата через фабрику."""

    user_id: UUID
    folder_id: UUID | None
    name: str | None
    settings: ChatSettings


class MockModel:
    def __init__(self, model_id: UUID, name: str) -> None:
        self.model_id: UUID = model_id
        self.name: str = name


class MockChat:
    def __init__(self, chat_id: UUID) -> None:
        self.chat_id: UUID = chat_id


@pytest.mark.asyncio
class TestCreateChatUseCase:
    chat_id: UUID
    user_id: UUID
    model_id: UUID
    folder_id: UUID
    chat_repository: AsyncMock
    chat_factory: Mock
    model_repository: AsyncMock
    mock_chat: MockChat
    command: CreateChatCommand
    use_case: CreateChatUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.chat_id = uuid4()
        self.user_id = uuid4()
        self.model_id = uuid4()
        self.folder_id = uuid4()

        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.chat_factory = Mock(spec=IChatFactory)
        self.model_repository = AsyncMock(spec=IModelRepository)

        self.mock_chat = MockChat(self.chat_id)
        self.chat_factory.create.return_value = self.mock_chat

        self.model_repository.get_by_name.return_value = MockModel(
            self.model_id, "gemini-2.5-flash-lite"
        )

        self.command = CreateChatCommand(user_id=self.user_id)
        self.use_case = CreateChatUseCase(
            self.chat_factory, self.chat_repository, self.model_repository
        )

    async def test_create_chat_success(self) -> None:
        """Проверяем успешное создание чата."""
        result: UUID = await self.use_case.execute(self.command)

        assert result == self.chat_id
        self.model_repository.get_by_name.assert_awaited_once_with(
            "gemini-2.5-flash-lite"
        )
        self.chat_factory.create.assert_called_once()
        self.chat_repository.add.assert_awaited_once_with(self.mock_chat)

    async def test_create_chat_calls_factory_with_correct_params(self) -> None:
        """Проверяем, что фабрика вызывается с правильными параметрами."""
        await self.use_case.execute(self.command)

        expected_params = CreateChatFactoryParams(
            user_id=self.user_id,
            folder_id=None,
            name=None,
            settings=ChatSettings(
                model_id=self.model_id,
                system_prompt="You are a helpful assistant",
                max_context_messages=20,
            ),
        )

        call_args = self.chat_factory.create.call_args
        actual_params = CreateChatFactoryParams(
            user_id=call_args.kwargs["user_id"],
            folder_id=call_args.kwargs["folder_id"],
            name=call_args.kwargs["name"],
            settings=call_args.kwargs["settings"],
        )

        assert actual_params == expected_params
