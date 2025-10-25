from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.datetime import DateTime

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
)
from luminary.chat.application.usecases.command.create_chat_use_case import (
    CreateChatUseCase,
)
from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)


@dataclass(frozen=True)
class CreateChatFactoryParams:
    user_id: UUID
    folder_id: UUID | None
    name: str | None
    settings: ChatSettings


class MockModel:
    def __init__(self, model_id: UUID, name: str) -> None:
        self.model_id: UUID = model_id
        self.name: str = name


@pytest.mark.asyncio
class TestCreateChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.chat_id = uuid4()
        self.user_id = uuid4()
        self.model_id = uuid4()
        self.folder_id = uuid4()

        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.chat_factory = Mock(spec=IChatFactory)
        self.model_repository = AsyncMock(spec=IModelRepository)

        self.command = CreateChatCommand(user_id=self.user_id)

        self.use_case = CreateChatUseCase(
            self.chat_factory, self.chat_repository, self.model_repository
        )

    def make_chat(
        self,
        chat_id: UUID | None = None,
        user_id: UUID | None = None,
        model_id: UUID | None = None,
    ) -> Chat:
        return Chat(
            chat_id=chat_id or self.chat_id,
            user_id=user_id or self.user_id,
            folder_id=self.folder_id,
            created_at=DateTime(datetime.now(UTC)),
            info=ChatInfo(name="Test Chat"),
            settings=ChatSettings(
                model_id=model_id or self.model_id,
                system_prompt="Test prompt",
                max_context_messages=10,
            ),
        )

    async def test_create_chat_success(self) -> None:
        chat = self.make_chat()
        model = MockModel(model_id=self.model_id, name="gemini-2.5-flash-lite")

        self.chat_factory.create.return_value = chat
        self.model_repository.get_by_name.return_value = model

        result = await self.use_case.execute(self.command)

        assert result == self.chat_id
        self.model_repository.get_by_name.assert_awaited_once_with(
            "gemini-2.5-flash-lite"
        )
        self.chat_factory.create.assert_called_once()
        self.chat_repository.add.assert_awaited_once_with(chat)

    async def test_create_chat_calls_factory_with_correct_params(self) -> None:
        chat = self.make_chat()
        model = MockModel(model_id=self.model_id, name="gemini-2.5-flash-lite")

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
