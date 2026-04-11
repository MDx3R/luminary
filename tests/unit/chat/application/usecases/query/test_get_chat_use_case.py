"""Unit tests for GetChatByIdUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.chat.application.dtos.read_models import ChatReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatByIdQuery,
)
from luminary.chat.application.usecases.query.get_chat_use_case import (
    GetChatByIdUseCase,
)


@pytest.mark.asyncio
class TestGetChatByIdUseCase:
    async def test_returns_read_model_from_repository(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()
        read_model = ChatReadModel(
            id=chat_id,
            name="Chat",
            folder_id=None,
            assistant_id=None,
            assistant_name=None,
            model_id=uuid4(),
            max_context_messages=10,
            sources=(),
            created_at=datetime.now(UTC),
        )
        read_repo: AsyncMock = AsyncMock(spec=IChatReadRepository)
        read_repo.get_by_id = AsyncMock(return_value=read_model)

        use_case = GetChatByIdUseCase(read_repository=read_repo)
        query = GetChatByIdQuery(user_id=user_id, chat_id=chat_id)

        result = await use_case.execute(query)

        assert result == read_model
        read_repo.get_by_id.assert_awaited_once_with(chat_id, user_id)
