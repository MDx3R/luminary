"""Unit tests for ListAssistantsUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.list_assistants_use_case import (
    ListAssistantsQuery,
)
from luminary.assistant.application.usecases.query.list_assistants_use_case import (
    ListAssistantsUseCase,
)


@pytest.mark.asyncio
class TestListAssistantsUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        user_id = uuid4()
        read_models: list[AssistantSummaryReadModel] = [
            AssistantSummaryReadModel(
                id=uuid4(),
                name="A1",
                description="D1",
                type="personal",
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.list_by_owner = AsyncMock(return_value=read_models)

        use_case = ListAssistantsUseCase(read_repository=read_repo)
        query = ListAssistantsQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert list(result) == read_models
        read_repo.list_by_owner.assert_awaited_once_with(user_id)
