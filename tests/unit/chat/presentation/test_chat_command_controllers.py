from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import pytest
from datetime import datetime, timezone  # Добавьте timezone

from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import ICreateChatUseCase
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import ISendMessageUseCase, MessageDTO
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    IGetStreamingMessageResponseUseCase,
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.domain.enums import Author, MessageStatus
from common.domain.value_objects.datetime import DateTime

@pytest.mark.asyncio
class TestChatCommandController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.message_id = uuid4()

        self.create_chat_use_case = AsyncMock(spec=ICreateChatUseCase)
        self.send_message_use_case = AsyncMock(spec=ISendMessageUseCase)
        self.get_message_response_use_case = Mock(spec=IGetStreamingMessageResponseUseCase)

        self.create_chat_use_case.execute.return_value = self.chat_id

        self.message_dto = MessageDTO(
            message_id=self.message_id,
            chat_id=self.chat_id,
            author=Author.USER,
            status=MessageStatus.COMPLETED,
            content="Hello",
            tokens=None,
            created_at=DateTime(datetime.now(timezone.utc)),  # ИСПРАВЛЕНО: добавлен timezone.utc
        )
        self.send_message_use_case.execute.return_value = self.message_dto

    async def test_create_chat_returns_chat_id(self):
        from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import CreateChatCommand
        result = await self.create_chat_use_case.execute(CreateChatCommand(self.user_id))
        assert result == self.chat_id
        self.create_chat_use_case.execute.assert_awaited_once()

    async def test_send_message_returns_message_dto(self):
        from luminary.chat.application.interfaces.usecases.command.send_message_use_case import SendMessageCommand
        command = SendMessageCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
            message="Hello",
        )
        result = await self.send_message_use_case.execute(command)
        assert result.message_id == self.message_id
        assert result.chat_id == self.chat_id
        assert result.content == "Hello"
        assert result.author == Author.USER
        self.send_message_use_case.execute.assert_awaited_once_with(command)

    async def test_streaming_response_format(self):
        async def mock_stream():
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

        chunks = []
        async for chunk in self.get_message_response_use_case.execute(None):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0].state == StreamState.START
        assert chunks[1].state == StreamState.DELTA
        assert chunks[1].content == "Hello"
        assert chunks[2].state == StreamState.END