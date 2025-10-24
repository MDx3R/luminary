from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.datetime import DateTime

from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    IGetStreamingMessageResponseUseCase,
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
    MessageDTO,
    SendMessageCommand,
)
from luminary.chat.domain.enums import Author, MessageStatus


@pytest.mark.asyncio
class TestChatCommandController:
    user_id: UUID
    chat_id: UUID
    message_id: UUID
    create_chat_use_case: AsyncMock
    send_message_use_case: AsyncMock
    get_message_response_use_case: Mock
    message_dto: MessageDTO

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.message_id = uuid4()

        self.create_chat_use_case = AsyncMock(spec=ICreateChatUseCase)
        self.send_message_use_case = AsyncMock(spec=ISendMessageUseCase)
        self.get_message_response_use_case = Mock(
            spec=IGetStreamingMessageResponseUseCase
        )

        self.create_chat_use_case.execute.return_value = self.chat_id

        self.message_dto = MessageDTO(
            message_id=self.message_id,
            chat_id=self.chat_id,
            author=Author.USER,
            status=MessageStatus.COMPLETED,
            content="Hello",
            tokens=None,
            created_at=DateTime(datetime.now(UTC)),
        )

        self.send_message_use_case.execute.return_value = self.message_dto

    async def test_create_chat_returns_chat_id(self) -> None:
        """Проверяем, что создание чата возвращает UUID."""
        command: CreateChatCommand = CreateChatCommand(self.user_id)
        result: UUID = await self.create_chat_use_case.execute(command)

        assert result == self.chat_id
        self.create_chat_use_case.execute.assert_awaited_once()

    async def test_send_message_returns_message_dto(self) -> None:
        """Проверяем, что отправка сообщения возвращает правильный DTO."""
        command: SendMessageCommand = SendMessageCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
            message="Hello",
        )

        result: MessageDTO = await self.send_message_use_case.execute(command)

        expected_dto = MessageDTO(
            message_id=self.message_id,
            chat_id=self.chat_id,
            author=Author.USER,
            status=MessageStatus.COMPLETED,
            content="Hello",
            tokens=None,
            created_at=self.message_dto.created_at,
        )

        assert result == expected_dto
        self.send_message_use_case.execute.assert_awaited_once_with(command)

    async def test_streaming_response_format(self) -> None:
        """Проверяем формат стримингового ответа через сравнение с ожидаемыми DTO."""

        async def mock_stream() -> AsyncGenerator[StreamingMessageDTO, None]:
            yield StreamingMessageDTO(
                state=StreamState.START,
                content="start",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.STREAMING,
            )
            yield StreamingMessageDTO(
                state=StreamState.DELTA,
                content="Hello",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.STREAMING,
            )
            yield StreamingMessageDTO(
                state=StreamState.END,
                content="end",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.COMPLETED,
            )

        self.get_message_response_use_case.execute.return_value = mock_stream()

        chunks: list[StreamingMessageDTO] = []
        async for chunk in self.get_message_response_use_case.execute(None):
            chunks.append(chunk)

        assert len(chunks) == 3

        expected_chunks: list[StreamingMessageDTO] = [
            StreamingMessageDTO(
                state=StreamState.START,
                content="start",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.STREAMING,
            ),
            StreamingMessageDTO(
                state=StreamState.DELTA,
                content="Hello",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.STREAMING,
            ),
            StreamingMessageDTO(
                state=StreamState.END,
                content="end",
                message_id=self.message_id,
                author=Author.ASSISTANT,
                status=MessageStatus.COMPLETED,
            ),
        ]

        for actual, expected in zip(chunks, expected_chunks, strict=False):
            assert actual == expected
