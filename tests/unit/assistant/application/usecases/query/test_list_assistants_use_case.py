"""Unit tests for ListUserAssistantsUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.list_assistants_use_case import (
    ListUserAssistantsQuery,
)
from luminary.assistant.application.usecases.query.list_assistants_use_case import (
    ListUserAssistantsUseCase,
)


@pytest.mark.asyncio
class TestListUserAssistantsUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        # Arrange
        user_id = uuid4()
        read_models: list[AssistantSummaryReadModel] = [
            AssistantSummaryReadModel(
                id=uuid4(),
                name="A1",
                description="D1",
                type="personal",
                tags=[],
            ),
            AssistantSummaryReadModel(
                id=uuid4(),
                name="System Bot",
                description="System",
                type="system",
                tags=[],
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.list_for_user = AsyncMock(return_value=read_models)

        use_case = ListUserAssistantsUseCase(read_repository=read_repo)
        query = ListUserAssistantsQuery(user_id=user_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert list(result) == read_models
        read_repo.list_for_user.assert_awaited_once_with(user_id)
