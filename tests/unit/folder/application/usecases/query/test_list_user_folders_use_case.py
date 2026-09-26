"""Unit tests for ListUserFoldersUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.folder.application.dtos.read_models import FolderSummaryReadModel
from luminary.folder.application.interfaces.repositories.folder_read_repository import (
    IFolderReadRepository,
)
from luminary.folder.application.interfaces.usecases.query.list_user_folders_use_case import (
    ListUserFoldersQuery,
)
from luminary.folder.application.usecases.query.list_user_folders_use_case import (
    ListUserFoldersUseCase,
)


@pytest.mark.asyncio
class TestListUserFoldersUseCase:
    async def test_returns_sequence_from_repository(self) -> None:
        user_id = uuid4()
        read_models: list[FolderSummaryReadModel] = [
            FolderSummaryReadModel(
                id=uuid4(),
                name="F1",
                description=None,
                created_at=datetime.now(UTC),
            ),
        ]
        read_repo: AsyncMock = AsyncMock(spec=IFolderReadRepository)
        read_repo.list_by_owner = AsyncMock(return_value=read_models)

        use_case = ListUserFoldersUseCase(read_repository=read_repo)
        query = ListUserFoldersQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert list(result) == read_models
        read_repo.list_by_owner.assert_awaited_once_with(user_id)
