"""Unit tests for ListUserChatsUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.chat.application.dtos.read_models import ChatSummaryReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.list_user_chats_use_case import (
    ListUserChatsQuery,
)
from luminary.chat.application.usecases.query.list_user_chats_use_case import (
    ListUserChatsUseCase,
)


@pytest.mark.asyncio
class TestListUserChatsUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        user_id = uuid4()
        read_models: list[ChatSummaryReadModel] = [
            ChatSummaryReadModel(
                id=uuid4(),
                name="C1",
                model_id=uuid4(),
                created_at=datetime.now(UTC),
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IChatReadRepository)
        read_repo.list_standalone_by_owner = AsyncMock(
            return_value=read_models
        )

        use_case = ListUserChatsUseCase(read_repository=read_repo)
        query = ListUserChatsQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert list(result) == read_models
        read_repo.list_standalone_by_owner.assert_awaited_once_with(user_id)
