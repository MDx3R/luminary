from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.delete_folder_use_case import (
    DeleteFolderCommand,
)
from luminary.folder.application.usecases.command.delete_folder_use_case import (
    DeleteFolderUseCase,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


@pytest.mark.asyncio
class TestDeleteFolderUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.folder_id = uuid4()

        self.folder = make_folder(
            folder_id=self.folder_id,
            owner_id=self.user_id,
        )

        self.access_policy: Mock = Mock(spec=IFolderAccessPolicy)
        self.repository: AsyncMock = AsyncMock(
            spec=IFolderRepository,
            get_by_id=AsyncMock(return_value=self.folder),
        )

        self.command = DeleteFolderCommand(
            user_id=self.user_id,
            folder_id=self.folder_id,
        )

        self.use_case = DeleteFolderUseCase(
            repository=self.repository,
            access_policy=self.access_policy,
        )

    async def test_calls_repository_get_by_id_with_folder_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.get_by_id.assert_awaited_once_with(
            FolderId(self.folder_id)
        )

    async def test_calls_access_policy_with_user_and_folder(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.folder
        )

    async def test_calls_repository_save_with_soft_deleted_folder(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.save.assert_awaited_once_with(self.folder)
        assert self.folder.is_deleted

    async def test_raises_not_found_when_folder_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(
            FolderId(self.folder_id)
        )

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.folder.id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)
