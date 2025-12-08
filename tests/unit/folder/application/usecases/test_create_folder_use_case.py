from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.assistant.domain.entity.assisnant import AssistantId
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


class TestCreateFolderUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.assistant_id = AssistantId(uuid4())

        self.folder_repository = AsyncMock(spec=IFolderRepository)
        self.folder_factory = Mock(spec=IFolderFactory)

        self.command = CreateFolderCommand(
            user_id=self.user_id.value,
            name="Test Folder",
            description="Test Description",
            assistant_id=self.assistant_id.value,
        )

        self.use_case = CreateFolderUseCase(self.folder_factory, self.folder_repository)

    @pytest.mark.asyncio
    async def test_create_folder_success(self):
        folder = make_folder()
        self.folder_factory.create.return_value = folder

        result = await self.use_case.execute(self.command)
        assert result == folder.id.value

        self.folder_factory.create.assert_called_once_with(
            "Test Folder", "Test Description", self.user_id, self.assistant_id
        )
        self.folder_repository.add.assert_awaited_once_with(folder)
