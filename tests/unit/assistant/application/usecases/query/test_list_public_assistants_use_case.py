"""Unit tests for ListPublicAssistantsUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.list_public_assistants_use_case import (
    ListPublicAssistantsQuery,
)
from luminary.assistant.application.usecases.query.list_public_assistants_use_case import (
    ListPublicAssistantsUseCase,
)


@pytest.mark.asyncio
class TestListPublicAssistantsUseCase:
    async def test_returns_public_assistants_from_repository(self) -> None:
        # Arrange
        read_models: list[AssistantSummaryReadModel] = [
            AssistantSummaryReadModel(
                id=uuid4(), name="P1", description="D1", type="public", tags=[]
            ),
            AssistantSummaryReadModel(
                id=uuid4(), name="P2", description="D2", type="public", tags=[]
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.list_public = AsyncMock(return_value=read_models)

        use_case = ListPublicAssistantsUseCase(read_repository=read_repo)
        query = ListPublicAssistantsQuery(offset=0, limit=20)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert list(result) == read_models
        read_repo.list_public.assert_awaited_once_with(0, 20)

    async def test_passes_pagination_params_to_repository(self) -> None:
        # Arrange
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.list_public = AsyncMock(return_value=[])

        use_case = ListPublicAssistantsUseCase(read_repository=read_repo)
        query = ListPublicAssistantsQuery(offset=40, limit=10)

        # Act
        await use_case.execute(query)

        # Assert
        read_repo.list_public.assert_awaited_once_with(40, 10)

    async def test_returns_empty_when_no_public_assistants(self) -> None:
        # Arrange
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.list_public = AsyncMock(return_value=[])

        use_case = ListPublicAssistantsUseCase(read_repository=read_repo)
        query = ListPublicAssistantsQuery()

        # Act
        result = await use_case.execute(query)

        # Assert
        assert list(result) == []
