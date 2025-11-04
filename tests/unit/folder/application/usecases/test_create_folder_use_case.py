from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    CreateFolderCommand,
)
from luminary.folder.application.usecases.command.create_folder_use_case import (
    CreateFolderUseCase,
)


class TestCreateFolderUseCase:
    @pytest.fixture
    def setup(self):
        self.folder_factory = Mock()
        self.folder_repository = AsyncMock()
        self.use_case = CreateFolderUseCase(self.folder_factory, self.folder_repository)
        
        self.command = CreateFolderCommand(
            user_id=uuid4(),
            name="Test Folder",
            description="Test Description",
            model_id=uuid4(),
            assistant_id=uuid4()
        )
        
        return self

    @pytest.mark.asyncio
    async def test_create_folder_success(self, setup):
        folder = Mock()
        folder.folder_id = uuid4()
        setup.folder_factory.create.return_value = folder
        
        result = await setup.use_case.execute(setup.command)
        
        assert result == folder.folder_id
        setup.folder_factory.create.assert_called_once_with(
            setup.command.name,
            setup.command.description,
            setup.command.user_id,
            setup.command.model_id,
            setup.command.assistant_id
        )
        setup.folder_repository.add.assert_awaited_once_with(folder)