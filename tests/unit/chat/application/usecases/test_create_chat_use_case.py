from unittest.mock import AsyncMock, Mock
from uuid import uuid4

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


@pytest.mark.asyncio
class TestCreateChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.name = "Test Chat"

        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
            name=self.name,
        )

        self.chat_factory: Mock = Mock(
            spec=IChatFactory, create=Mock(return_value=self.chat)
        )
        self.chat_repository: AsyncMock = AsyncMock(spec=IChatRepository)

        self.command = CreateChatCommand(
            user_id=self.user_id,
            folder_id=None,
            name=self.name,
            assistant_id=None,
        )

        self.use_case = CreateChatUseCase(
            chat_factory=self.chat_factory,
            chat_repository=self.chat_repository,
        )

    async def test_calls_factory_with_correct_dto(self) -> None:
        await self.use_case.execute(self.command)

        self.chat_factory.create.assert_called_once()
        call_args = self.chat_factory.create.call_args[0][0]
        assert isinstance(call_args, ChatFactoryDTO)
        assert call_args.user_id == UserId(self.user_id)
        assert call_args.folder_id is None
        assert call_args.name == self.name
        assert call_args.assistant_id is None

    async def test_calls_repository_add_with_created_chat(self) -> None:
        await self.use_case.execute(self.command)

        self.chat_repository.add.assert_awaited_once_with(self.chat)

    async def test_returns_created_chat_id(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.chat_id
