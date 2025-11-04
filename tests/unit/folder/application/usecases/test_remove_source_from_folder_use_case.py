from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError

from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    RemoveSourceFromFolderCommand,
)
from luminary.folder.application.usecases.command.remove_source_from_folder_use_case import (
    RemoveSourceFromFolderUseCase,
)


class TestRemoveSourceFromFolderUseCase:
    @pytest.fixture
    def setup(self):
        self.folder_access_policy = Mock()
        self.folder_repository = AsyncMock()
        
        self.use_case = RemoveSourceFromFolderUseCase(
            self.folder_access_policy,
            self.folder_repository
        )
        
        self.command = RemoveSourceFromFolderCommand(
            user_id=uuid4(),
            folder_id=uuid4(),
            source_id=uuid4()
        )
        
        return self

    @pytest.mark.asyncio
    async def test_remove_source_from_folder_success(self, setup):
        # Arrange
        folder = Mock()
        folder.has_source.return_value = True  # Source exists
        
        setup.folder_repository.get_by_id.return_value = folder

        # Act
        await setup.use_case.execute(setup.command)

        # Assert
        setup.folder_repository.get_by_id.assert_awaited_once_with(setup.command.folder_id)
        setup.folder_access_policy.assert_is_allowed.assert_called_once_with(
            setup.command.user_id, folder
        )
        folder.remove_source.assert_called_once_with(setup.command.source_id)
        setup.folder_repository.save.assert_awaited_once_with(folder)

    @pytest.mark.asyncio
    async def test_remove_source_from_folder_source_not_exists(self, setup):
        # Arrange
        folder = Mock()
        folder.has_source.return_value = False  # Source doesn't exist
        
        setup.folder_repository.get_by_id.return_value = folder

        # Act
        await setup.use_case.execute(setup.command)

        # Assert
        setup.folder_repository.get_by_id.assert_awaited_once_with(setup.command.folder_id)
        setup.folder_access_policy.assert_is_allowed.assert_called_once_with(
            setup.command.user_id, folder
        )
        folder.remove_source.assert_not_called()  # Should not call remove_source
        setup.folder_repository.save.assert_not_awaited()  # Should not save

    @pytest.mark.asyncio
    async def test_remove_source_folder_access_denied_raises(self, setup):
        # Arrange
        folder = Mock()
        setup.folder_repository.get_by_id.return_value = folder
        setup.folder_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            setup.command.folder_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await setup.use_case.execute(setup.command)

        setup.folder_repository.get_by_id.assert_awaited_once_with(setup.command.folder_id)
        folder.remove_source.assert_not_called()
        setup.folder_repository.save.assert_not_awaited()