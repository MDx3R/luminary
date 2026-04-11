"""Unit tests for ListChatMessagesUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.chat.application.dtos.read_models import MessageReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.list_chat_messages_use_case import (
    ListChatMessagesQuery,
)
from luminary.chat.application.usecases.query.list_chat_messages_use_case import (
    ListChatMessagesUseCase,
)


@pytest.mark.asyncio
class TestListChatMessagesUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()
        read_models: list[MessageReadModel] = [
            MessageReadModel(
                id=uuid4(),
                chat_id=chat_id,
                role="user",
                status="completed",
                content="Hi",
                model_id=uuid4(),
                tokens=1,
                created_at=datetime.now(UTC),
                edited_at=datetime.now(UTC),
                attachments=(),
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IChatReadRepository)
        read_repo.list_messages = AsyncMock(return_value=read_models)

        use_case = ListChatMessagesUseCase(read_repository=read_repo)
        query = ListChatMessagesQuery(
            user_id=user_id, chat_id=chat_id, limit=50, before=None
        )

        result = await use_case.execute(query)

        assert list(result) == read_models
        read_repo.list_messages.assert_awaited_once_with(
            chat_id, user_id, limit=50, before=None
        )
