from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import pytest
from common.application.exceptions import AccessPolicyError

from luminary.folder.application.usecases.command.add_source_to_folder_use_case import AddSourceToFolderUseCase
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import AddSourceToFolderCommand

class TestAddSourceToFolderUseCase:
    @pytest.fixture
    def setup(self):
        self.folder_access_policy = Mock()
        self.folder_repository = AsyncMock()
        self.source_access_policy = Mock()
        self.source_repository = AsyncMock()
        
        self.use_case = AddSourceToFolderUseCase(
            self.folder_access_policy,
            self.folder_repository,
            self.source_access_policy,
            self.source_repository
        )
        
        self.command = AddSourceToFolderCommand(
            user_id=uuid4(),
            folder_id=uuid4(),
            source_id=uuid4()
        )
        
        return self

    @pytest.mark.asyncio
    async def test_add_source_to_folder_success(self, setup):
        # Arrange
        folder = Mock()
        folder.has_source.return_value = False
        
        source = Mock()
        
        setup.folder_repository.get_by_id.return_value = folder
        setup.source_repository.get_by_id.return_value = source

        # Act
        await setup.use_case.execute(setup.command)

        # Assert
        setup.folder_repository.get_by_id.assert_awaited_once_with(setup.command.folder_id)
        setup.folder_access_policy.assert_is_allowed.assert_called_once_with(
            setup.command.user_id, folder
        )
        setup.source_repository.get_by_id.assert_awaited_once_with(setup.command.source_id)
        setup.source_access_policy.assert_is_allowed.assert_called_once_with(
            setup.command.user_id, source
        )
        folder.add_source.assert_called_once_with(setup.command.source_id)
        setup.folder_repository.save.assert_awaited_once_with(folder)

    @pytest.mark.asyncio
    async def test_add_source_to_folder_already_exists(self, setup):
        # Arrange
        folder = Mock()
        folder.has_source.return_value = True  # Source already exists
        
        source = Mock()
        
        setup.folder_repository.get_by_id.return_value = folder
        setup.source_repository.get_by_id.return_value = source

        # Act
        await setup.use_case.execute(setup.command)

        # Assert
        folder.add_source.assert_called_once_with(setup.command.source_id)  # Still called
        setup.folder_repository.save.assert_awaited_once_with(folder)

    @pytest.mark.asyncio
    async def test_add_source_folder_access_denied_raises(self, setup):
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
        setup.source_repository.get_by_id.assert_not_awaited()
        setup.folder_repository.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_add_source_source_access_denied_raises(self, setup):
        # Arrange
        folder = Mock()
        source = Mock()
        
        setup.folder_repository.get_by_id.return_value = folder
        setup.source_repository.get_by_id.return_value = source
        setup.source_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            setup.command.source_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await setup.use_case.execute(setup.command)

        setup.source_repository.get_by_id.assert_awaited_once_with(setup.command.source_id)
        setup.folder_repository.save.assert_not_awaited()