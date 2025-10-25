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
from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from luminary.chat.domain.entity.message import Message
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
        self.message_id = uuid4()
        self.model_id = uuid4()

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

    def make_chat(
        self,
        chat_id: UUID | None = None,
        user_id: UUID | None = None,
        model_id: UUID | None = None,
    ) -> Chat:
        return Chat(
            chat_id=chat_id or self.chat_id,
            user_id=user_id or self.user_id,
            folder_id=uuid4(),
            created_at=DateTime(datetime.now(UTC)),
            info=ChatInfo(name="Test Chat"),
            settings=ChatSettings(
                model_id=model_id or self.model_id,
                system_prompt="Test prompt",
                max_context_messages=10,
            ),
        )

    def make_message(
        self,
        message_id: UUID | None = None,
        chat_id: UUID | None = None,
        model_id: UUID | None = None,
        content: str = "Test message",
    ) -> Message:
        return Message(
            message_id=message_id or self.message_id,
            chat_id=chat_id or self.chat_id,
            model_id=model_id or self.model_id,
            content=content,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

    async def test_send_message_success(self) -> None:
        chat = self.make_chat()
        message = self.make_message(content=self.command.message)

        self.chat_repository.get_by_id.return_value = chat
        self.message_factory.create.return_value = message

        expected_dto = MessageDTO(
            message_id=self.message_id,
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
        chat = self.make_chat()
        message = self.make_message()

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
        chat = self.make_chat()
        message = self.make_message()

        self.chat_repository.get_by_id.return_value = chat
        self.message_factory.create.return_value = message

        result = await self.use_case.execute(self.command)

        assert result.tokens is None
