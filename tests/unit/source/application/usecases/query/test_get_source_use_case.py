"""Unit tests for GetSourceByIdUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.application.interfaces.repositories.source_read_repository import (
    ISourceReadRepository,
)
from luminary.source.application.interfaces.usecases.query.get_source_use_case import (
    GetSourceByIdQuery,
)
from luminary.source.application.usecases.query.get_source_use_case import (
    GetSourceByIdUseCase,
)


@pytest.mark.asyncio
class TestGetSourceByIdUseCase:
    async def test_returns_read_model_from_repository(self) -> None:
        user_id = uuid4()
        source_id = uuid4()
        read_model = SourceReadModel(
            id=source_id,
            title="Test",
            type="file",
            fetch_status="fetched",
            created_at=datetime.now(UTC),
            file_id=uuid4(),
        )
        read_repo: AsyncMock = AsyncMock(spec=ISourceReadRepository)
        read_repo.get_by_id = AsyncMock(return_value=read_model)

        use_case = GetSourceByIdUseCase(read_repository=read_repo)
        query = GetSourceByIdQuery(user_id=user_id, source_id=source_id)

        result = await use_case.execute(query)

        assert result == read_model
        read_repo.get_by_id.assert_awaited_once_with(source_id, user_id)
