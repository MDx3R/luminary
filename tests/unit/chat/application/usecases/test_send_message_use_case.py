from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.datetime import DateTime

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
from luminary.chat.domain.interfaces.message_factory import IMessageFactory


class MockChatSettings:
    def __init__(self, model_id: UUID) -> None:
        self.model_id: UUID = model_id


class MockChat:
    def __init__(self, chat_id: UUID, model_id: UUID) -> None:
        self.chat_id: UUID = chat_id
        self.settings: MockChatSettings = MockChatSettings(model_id)


class MockMessage:
    def __init__(
        self, message_id: UUID, chat_id: UUID, model_id: UUID, content: str
    ) -> None:
        self.message_id: UUID = message_id
        self.chat_id: UUID = chat_id
        self.model_id: UUID = model_id
        self.content: str = content
        self.role: Author = Author.USER
        self.status: MessageStatus = MessageStatus.COMPLETED
        self.created_at: DateTime = DateTime(datetime.now(UTC))
        self.tokens: int | None = None


@pytest.mark.asyncio
class TestSendMessageUseCase:
    user_id: UUID
    chat_id: UUID
    message_id: UUID
    model_id: UUID
    chat: MockChat
    message: MockMessage
    message_factory: Mock
    uow: AsyncMock
    chat_repository: AsyncMock
    message_repository: AsyncMock
    command: SendMessageCommand
    use_case: SendMessageUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.message_id = uuid4()
        self.model_id = uuid4()

        self.chat = MockChat(self.chat_id, self.model_id)
        self.message = MockMessage(
            self.message_id, self.chat_id, self.model_id, "Hello!"
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

    async def test_send_message_success(self) -> None:
        """Проверяем успешную отправку сообщения через сравнение с DTO."""
        result: MessageDTO = await self.use_case.execute(self.command)

        expected_dto = MessageDTO(
            message_id=self.message_id,
            chat_id=self.chat_id,
            content="Hello!",
            author=Author.USER,
            status=MessageStatus.COMPLETED,
            tokens=None,
            created_at=self.message.created_at,
        )

        assert result == expected_dto
        self.chat_repository.get_by_id.assert_awaited_once_with(self.chat_id)
        self.message_repository.add.assert_awaited_once_with(self.message)

    async def test_send_message_calls_factory_with_correct_params(self) -> None:
        """Проверяем, что фабрика сообщений вызывается с правильными параметрами."""
        await self.use_case.execute(self.command)

        self.message_factory.create.assert_called_once_with(
            chat_id=self.chat.chat_id,
            model_id=self.chat.settings.model_id,
            role=Author.USER,
            content=self.command.message,
        )

    async def test_send_message_returns_dto_with_no_tokens(self) -> None:
        """Проверяем, что DTO возвращается без токенов."""
        result: MessageDTO = await self.use_case.execute(self.command)

        assert result.tokens is None
