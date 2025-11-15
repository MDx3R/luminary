from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
)
from luminary.chat.application.usecases.command.create_chat_use_case import (
    CreateChatUseCase,
)
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.domain.entity.model import ModelId


@dataclass(frozen=True)
class CreateChatFactoryParams:
    user_id: UUID
    folder_id: UUID | None
    name: str | None
    settings: ChatSettings


class MockModel:
    def __init__(self, id: ModelId, name: str) -> None:
        self.id = id
        self.name = name


@pytest.mark.asyncio
class TestCreateChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = UserId(uuid4())
        self.model_id = ModelId(uuid4())

        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.chat_factory = Mock(spec=IChatFactory)
        self.model_repository = AsyncMock(spec=IModelRepository)

        self.command = CreateChatCommand(user_id=self.user_id.value)

        self.use_case = CreateChatUseCase(
            self.chat_factory, self.chat_repository, self.model_repository
        )

    async def test_create_chat_success(self) -> None:
        chat = make_chat()
        model = MockModel(id=self.model_id, name="gemini-2.5-flash-lite")

        self.chat_factory.create.return_value = chat
        self.model_repository.get_by_name.return_value = model

        result = await self.use_case.execute(self.command)

        assert result == chat.id.value
        self.model_repository.get_by_name.assert_awaited_once_with(
            "gemini-2.5-flash-lite"
        )
        self.chat_factory.create.assert_called_once()
        self.chat_repository.add.assert_awaited_once_with(chat)

    async def test_create_chat_calls_factory_with_correct_params(self) -> None:
        chat = make_chat()
        model = MockModel(id=self.model_id, name="gemini-2.5-flash-lite")

        self.chat_factory.create.return_value = chat
        self.model_repository.get_by_name.return_value = model

        await self.use_case.execute(self.command)

        expected_data = ChatFactoryDTO(
            user_id=self.user_id,
            folder_id=None,
            name=None,
            settings=ChatSettings(
                model_id=self.model_id,
                system_prompt="You are a helpful assistant",
                max_context_messages=20,
            ),
        )

        self.chat_factory.create.assert_called_once_with(expected_data)
