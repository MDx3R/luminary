from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder
from tests.unit.source.utils import make_source

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderCommand,
)
from luminary.folder.application.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderUseCase,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import Source, SourceId


class TestAddSourceToFolderUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.folder_id = FolderId(uuid4())
        self.source_id = SourceId(uuid4())

        # Используем spec для правильных моков
        self.folder_access_policy = Mock(spec=IFolderAccessPolicy)
        self.folder_repository = AsyncMock(spec=IFolderRepository)
        self.source_access_policy = Mock(spec=ISourceAccessPolicy)
        self.source_repository = AsyncMock(spec=ISourceRepository)

        self.command = AddSourceToFolderCommand(
            user_id=self.user_id.value,
            folder_id=self.folder_id.value,
            source_id=self.source_id.value,
        )

        self.use_case = AddSourceToFolderUseCase(
            self.folder_access_policy,
            self.folder_repository,
            self.source_access_policy,
            self.source_repository,
        )

    @pytest.mark.asyncio
    async def test_add_source_to_folder_success(self):
        # Arrange
        folder = make_folder(
            folder_id=self.folder_id.value, owner_id=self.user_id.value
        )
        source = make_source(source_id=self.source_id.value)

        self.folder_repository.get_by_id.return_value = folder
        self.source_repository.get_by_id.return_value = source

        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.folder_repository.get_by_id.assert_awaited_once_with(self.folder_id)
        self.folder_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, folder
        )
        self.source_repository.get_by_id.assert_awaited_once_with(self.source_id)
        self.source_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, source
        )
        assert self.source_id in folder.sources
        self.folder_repository.save.assert_awaited_once_with(folder)

    @pytest.mark.asyncio
    async def test_add_source_to_folder_already_exists(self):
        # Arrange
        folder = make_folder(
            folder_id=self.folder_id.value, owner_id=self.user_id.value
        )
        source = make_source(source_id=self.source_id.value)
        folder.add_source(source_id=self.source_id)

        self.folder_repository.get_by_id.return_value = folder
        self.source_repository.get_by_id.return_value = source

        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.folder_repository.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_add_source_folder_access_denied_raises(self):
        # Arrange
        folder = Mock(spec=Folder)
        self.folder_repository.get_by_id.return_value = folder
        self.folder_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.folder_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.folder_repository.get_by_id.assert_awaited_once_with(self.folder_id)
        self.source_repository.get_by_id.assert_not_awaited()
        self.folder_repository.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_add_source_source_access_denied_raises(self, setup):
        # Arrange
        folder = Mock(spec=Folder)
        folder.has_source.return_value = False
        source = Mock(spec=Source)

        self.folder_repository.get_by_id.return_value = folder
        self.source_repository.get_by_id.return_value = source
        self.source_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.source_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.source_repository.get_by_id.assert_awaited_once_with(self.source_id)
        self.folder_repository.save.assert_not_awaited()
