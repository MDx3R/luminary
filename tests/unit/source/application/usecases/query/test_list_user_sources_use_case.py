"""Unit tests for ListUserSourcesUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.application.interfaces.repositories.source_read_repository import (
    ISourceReadRepository,
)
from luminary.source.application.interfaces.usecases.query.list_user_sources_use_case import (
    ListUserSourcesQuery,
)
from luminary.source.application.usecases.query.list_user_sources_use_case import (
    ListUserSourcesUseCase,
)


@pytest.mark.asyncio
class TestListUserSourcesUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        user_id = uuid4()
        read_models: list[SourceReadModel] = [
            SourceReadModel(
                id=uuid4(),
                title="S1",
                type="file",
                fetch_status="fetched",
                created_at=datetime.now(UTC),
                file_id=uuid4(),
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=ISourceReadRepository)
        read_repo.list_by_owner = AsyncMock(return_value=read_models)

        use_case = ListUserSourcesUseCase(read_repository=read_repo)
        query = ListUserSourcesQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert list(result) == read_models
        read_repo.list_by_owner.assert_awaited_once_with(user_id)
