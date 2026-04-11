"""Unit tests for GetAssistantByIdUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.assistant.application.dtos.read_models import AssistantReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.get_assistant_use_case import (
    GetAssistantByIdQuery,
)
from luminary.assistant.application.usecases.query.get_assistant_use_case import (
    GetAssistantByIdUseCase,
)


@pytest.mark.asyncio
class TestGetAssistantByIdUseCase:
    async def test_returns_read_model_from_repository(self) -> None:
        user_id = uuid4()
        assistant_id = uuid4()
        read_model = AssistantReadModel(
            id=assistant_id,
            name="A1",
            description="Desc",
            type="personal",
            prompt="You are...",
            created_at=datetime.now(UTC),
        )
        read_repo: AsyncMock = AsyncMock(spec=IAssistantReadRepository)
        read_repo.get_by_id = AsyncMock(return_value=read_model)

        use_case = GetAssistantByIdUseCase(read_repository=read_repo)
        query = GetAssistantByIdQuery(
            user_id=user_id, assistant_id=assistant_id
        )

        result = await use_case.execute(query)

        assert result == read_model
        read_repo.get_by_id.assert_awaited_once_with(assistant_id, user_id)
