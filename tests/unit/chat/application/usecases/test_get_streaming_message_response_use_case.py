from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from luminary.chat.application.interfaces.policies.chat_access_policy import IChatAccessPolicy
import pytest
from common.application.exceptions import NotFoundError
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from tests.unit.chat.utils import make_chat, make_message

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    GetMessageResponseCommand,
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.application.usecases.command.get_message_response_use_case import (
    GetStreamingMessageResponseUseCase,
)
from luminary.chat.domain.interfaces.message_factory import IMessageFactory
from luminary.model.application.interfaces.services.ai_provider import AIProvider


@pytest.mark.asyncio
class TestGetStreamingMessageResponseUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.message_id = uuid4()
        self.chat_id = uuid4()
        self.user_id = uuid4()

        self.message_factory = Mock(spec=IMessageFactory)
        self.uow = AsyncMock(spec=IUnitOfWork)
        self.ai_provider = AsyncMock(spec=AIProvider)
        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.message_repository = AsyncMock(spec=IMessageRepository)
        self.chat_access_policy = AsyncMock(spec=IChatAccessPolicy)

        self.command = GetMessageResponseCommand(
            message_id=self.message_id,
            chat_id=self.chat_id,
            user_id=self.user_id,
        )

        self.use_case = GetStreamingMessageResponseUseCase(
            self.message_factory,
            self.uow,
            self.ai_provider,
            self.chat_repository,
            self.message_repository,
            self.chat_access_policy,
        )

    @staticmethod
    async def _create_mock_ai_stream(*contents: str) -> AsyncGenerator[Any, None]:
        for content in contents:
            yield Mock(content=content)

    async def test_streaming_response_returns_start_delta_end_sequence(
        self,
    ) -> None:
        chat = make_chat(chat_id=self.chat_id)
        request = make_message(
            message_id=self.message_id, chat_id=self.chat_id, content="Hello AI"
        )
        response = make_message(content="")

        self.chat_repository.get_by_id.return_value = chat
        self.message_repository.get_by_id.return_value = request
        self.message_factory.create.return_value = response

        produced_chunks = ["Hello ", "world"]
        self.ai_provider.stream_completion.return_value = self._create_mock_ai_stream(
            *produced_chunks
        )

        chunks: list[StreamingMessageDTO] = []
        async for chunk in self.use_case.execute(self.command):
            chunks.append(chunk)

        assert (
            len(chunks) == len(produced_chunks) + 2
        )  # NOTE: start, message itself, end
        assert chunks[0].state == StreamState.START
        assert chunks[-1].state == StreamState.END

        delta_chunks = [c for c in chunks if c.state == StreamState.DELTA]
        assert len(delta_chunks) == len(produced_chunks)
        assert [
            i.content for i in delta_chunks
        ] == produced_chunks  # Check order is unchanged

    async def test_streaming_response_contains_message_id(self) -> None:
        chat = make_chat(chat_id=self.chat_id)
        request = make_message(message_id=self.message_id, chat_id=self.chat_id)
        response = make_message(content="Response", chat_id=self.chat_id)

        self.chat_repository.get_by_id.return_value = chat
        self.message_repository.get_by_id.return_value = request
        self.message_factory.create.return_value = response

        self.ai_provider.stream_completion.return_value = self._create_mock_ai_stream(
            "Test"
        )

        async for chunk in self.use_case.execute(self.command):
            assert chunk.message_id == response.message_id

    async def test_streaming_response_handles_not_found_error(self) -> None:
        chat = make_chat(chat_id=self.chat_id)

        request = make_message(chat_id=uuid4())  # Random chat_id

        self.chat_repository.get_by_id.return_value = chat
        self.message_repository.get_by_id.return_value = request

        with pytest.raises(NotFoundError):
            async for _ in self.use_case.execute(self.command):
                ...
