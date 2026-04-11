"""Unit tests for GetFolderByIdUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from luminary.folder.application.dtos.read_models import FolderReadModel
from luminary.folder.application.interfaces.repositories.folder_read_repository import (
    IFolderReadRepository,
)
from luminary.folder.application.interfaces.usecases.query.get_folder_use_case import (
    GetFolderByIdQuery,
)
from luminary.folder.application.usecases.query.get_folder_use_case import (
    GetFolderByIdUseCase,
)


@pytest.mark.asyncio
class TestGetFolderByIdUseCase:
    async def test_returns_read_model_from_repository(self) -> None:
        user_id = uuid4()
        folder_id = uuid4()
        read_model = FolderReadModel(
            id=folder_id,
            name="F1",
            description=None,
            assistant_id=None,
            assistant_name=None,
            editor=None,
            chats=(),
            sources=(),
            created_at=datetime.now(UTC),
        )
        read_repo: AsyncMock = AsyncMock(spec=IFolderReadRepository)
        read_repo.get_by_id = AsyncMock(return_value=read_model)

        use_case = GetFolderByIdUseCase(read_repository=read_repo)
        query = GetFolderByIdQuery(
            user_id=user_id, folder_id=folder_id
        )

        result = await use_case.execute(query)

        assert result == read_model
        read_repo.get_by_id.assert_awaited_once_with(folder_id, user_id)
