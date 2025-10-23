from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import pytest

from tests.unit.chat.utils import make_chat, make_message
from luminary.chat.application.interfaces.repositories.chat_repository import IChatRepository
from luminary.chat.application.interfaces.repositories.message_repository import IMessageRepository
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
    MessageDTO,
    SendMessageCommand,
)
from luminary.chat.application.usecases.command.send_message_use_case import SendMessageUseCase
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.interfaces.message_factory import IMessageFactory
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

@pytest.mark.asyncio
class TestSendMessageUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.message_id = uuid4()
        self.model_id = uuid4()

        self.chat = make_chat(
            chat_id=self.chat_id,
            model_id=self.model_id,
        )

        self.message = make_message(
            message_id=self.message_id,
            chat_id=self.chat_id,
            model_id=self.model_id,
            content="Hello!",
            role=Author.USER,
            status=MessageStatus.COMPLETED,
        )

        self.message_factory = Mock(spec=IMessageFactory)
        self.uow = AsyncMock(spec=IUnitOfWork)
        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.message_repository = AsyncMock(spec=IMessageRepository)

        self.message_factory.create.return_value = self.message
        self.chat_repository.get_by_id.return_value = self.chat

        self.command = SendMessageCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
            message="Hello!",
        )

        self.use_case = SendMessageUseCase(
            self.message_factory,
            self.uow,
            self.chat_repository,
            self.message_repository,
        )

    async def test_send_message_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, MessageDTO)
        assert result.message_id == self.message_id
        assert result.chat_id == self.chat_id
        assert result.content == "Hello!"
        assert result.author == Author.USER
        assert result.status == MessageStatus.COMPLETED

        self.chat_repository.get_by_id.assert_awaited_once_with(self.chat_id)
        self.message_repository.add.assert_awaited_once_with(self.message)

    async def test_send_message_calls_factory_with_correct_params(self):
        await self.use_case.execute(self.command)

        self.message_factory.create.assert_called_once_with(
            chat_id=self.chat.chat_id,
            model_id=self.chat.settings.model_id,
            role=Author.USER,
            content=self.command.message,
        )

    async def test_send_message_returns_dto_with_no_tokens(self):
        result = await self.use_case.execute(self.command)
        assert result.tokens is None
