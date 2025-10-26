from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from tests.unit.chat.utils import make_chat, make_message

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    MessageDTO,
    SendMessageCommand,
)
from luminary.chat.application.usecases.command.send_message_use_case import (
    SendMessageUseCase,
)
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)


@pytest.mark.asyncio
class TestSendMessageUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()

        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.message_repository = AsyncMock(spec=IMessageRepository)
        self.message_factory = Mock(spec=IMessageFactory)
        self.uow = AsyncMock(spec=IUnitOfWork)

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

    async def test_send_message_success(self) -> None:
        chat = make_chat(chat_id=self.chat_id)
        message = make_message(chat_id=chat.chat_id, content=self.command.message)

        self.chat_repository.get_by_id.return_value = chat
        self.message_factory.create.return_value = message

        expected_dto = MessageDTO(
            message_id=message.message_id,
            chat_id=self.chat_id,
            content="Hello!",
            author=Author.USER,
            status=MessageStatus.COMPLETED,
            tokens=None,
            created_at=message.created_at,
        )

        result = await self.use_case.execute(self.command)

        assert result == expected_dto
        self.chat_repository.get_by_id.assert_awaited_once_with(self.chat_id)
        self.message_repository.add.assert_awaited_once_with(message)

    async def test_send_message_calls_factory_with_correct_params(self) -> None:
        chat = make_chat(chat_id=self.chat_id)
        message = make_message(chat_id=chat.chat_id)

        self.chat_repository.get_by_id.return_value = chat
        self.message_factory.create.return_value = message

        await self.use_case.execute(self.command)

        self.message_factory.create.assert_called_once_with(
            MessageFactoryDTO(
                chat_id=chat.chat_id,
                model_id=chat.settings.model_id,
                role=Author.USER,
                content=self.command.message,
            )
        )

    async def test_send_message_returns_dto_with_no_tokens(self) -> None:
        chat = make_chat(chat_id=self.chat_id)
        message = make_message(chat_id=chat.chat_id)

        self.chat_repository.get_by_id.return_value = chat
        self.message_factory.create.return_value = message

        result = await self.use_case.execute(self.command)

        assert result.tokens is None
