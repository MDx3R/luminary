from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    RemoveSourceFromFolderCommand,
)
from luminary.folder.application.usecases.command.remove_source_from_folder_use_case import (
    RemoveSourceFromFolderUseCase,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class TestRemoveSourceFromFolderUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.folder_id = FolderId(uuid4())
        self.source_id = SourceId(uuid4())

        self.folder_access_policy = Mock(spec=IFolderAccessPolicy)  # spec добавлен
        self.folder_repository = AsyncMock(spec=IFolderRepository)

        self.command = RemoveSourceFromFolderCommand(
            user_id=self.user_id.value,
            folder_id=self.folder_id.value,
            source_id=self.source_id.value,
        )
        self.use_case = RemoveSourceFromFolderUseCase(
            self.folder_access_policy, self.folder_repository
        )

    @pytest.mark.asyncio
    async def test_remove_source_from_folder_success(self):
        # Arrange
        folder = Mock(spec=Folder)
        folder.has_source.return_value = True  # Source exists

        self.folder_repository.get_by_id.return_value = folder

        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.folder_repository.get_by_id.assert_awaited_once_with(self.folder_id)
        self.folder_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, folder
        )
        folder.remove_source.assert_called_once_with(self.source_id)
        self.folder_repository.save.assert_awaited_once_with(folder)

    @pytest.mark.asyncio
    async def test_remove_source_from_folder_source_not_exists(self, setup):
        # Arrange
        folder = Mock(spec=Folder)
        folder.has_source.return_value = False  # Source doesn't exist

        self.folder_repository.get_by_id.return_value = folder

        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.folder_repository.get_by_id.assert_awaited_once_with(self.folder_id)
        self.folder_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, folder
        )
        folder.remove_source.assert_not_called()  # Should not call remove_source
        self.folder_repository.save.assert_not_awaited()  # Should not save

    @pytest.mark.asyncio
    async def test_remove_source_folder_access_denied_raises(self, setup):
        # Arrange
        folder = Mock(spec=Folder)
        folder.has_source.return_value = False
        self.folder_repository.get_by_id.return_value = folder
        self.folder_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.folder_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.folder_repository.get_by_id.assert_awaited_once_with(self.folder_id)
        folder.remove_source.assert_not_called()
        self.folder_repository.save.assert_not_awaited()
