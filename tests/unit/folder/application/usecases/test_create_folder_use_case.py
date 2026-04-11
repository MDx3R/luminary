from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    CreateFolderCommand,
)
from luminary.folder.application.usecases.command.create_folder_use_case import (
    CreateFolderUseCase,
)
from luminary.folder.domain.interfaces.folder_factory import IFolderFactory


@pytest.mark.asyncio
class TestCreateFolderUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.folder_id = uuid4()
        self.name = "Test Folder"
        self.description = "Test Description"

        self.folder = make_folder(
            folder_id=self.folder_id,
            owner_id=self.user_id,
        )

        self.folder_factory: Mock = Mock(
            spec=IFolderFactory, create=Mock(return_value=self.folder)
        )
        self.folder_repository: AsyncMock = AsyncMock(
            spec=IFolderRepository
        )

        self.command = CreateFolderCommand(
            user_id=self.user_id,
            name=self.name,
            description=self.description,
            assistant_id=None,
        )

        self.use_case = CreateFolderUseCase(
            folder_factory=self.folder_factory,
            folder_repository=self.folder_repository,
        )

    async def test_calls_factory_with_correct_params(self) -> None:
        await self.use_case.execute(self.command)

        self.folder_factory.create.assert_called_once_with(
            name=self.name,
            description=self.description,
            user_id=UserId(self.user_id),
            assistant_id=None,
        )

    async def test_calls_repository_add_with_created_folder(self) -> None:
        await self.use_case.execute(self.command)

        self.folder_repository.add.assert_awaited_once_with(self.folder)

    async def test_returns_created_folder_id(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.folder_id
