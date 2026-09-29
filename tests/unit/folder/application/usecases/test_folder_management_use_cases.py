from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.reorder_folders_use_case import (
    ReorderFoldersCommand,
)
from luminary.folder.application.interfaces.usecases.command.set_folder_collapsed_use_case import (
    SetFolderCollapsedCommand,
)
from luminary.folder.application.usecases.command.reorder_folders_use_case import (
    ReorderFoldersUseCase,
)
from luminary.folder.application.usecases.command.set_folder_collapsed_use_case import (
    SetFolderCollapsedUseCase,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


@pytest.mark.asyncio
async def test_set_collapsed_persists_owned_folder() -> None:
    owner_id = uuid4()
    folder = make_folder(owner_id=owner_id)
    repository = AsyncMock(spec=IFolderRepository)
    repository.get_by_id.return_value = folder
    access_policy = Mock(spec=IFolderAccessPolicy)

    use_case = SetFolderCollapsedUseCase(repository, access_policy)
    await use_case.execute(
        SetFolderCollapsedCommand(owner_id, folder.id.value, collapsed=True)
    )

    assert folder.collapsed is True
    access_policy.assert_is_allowed.assert_called_once_with(UserId(owner_id), folder)
    repository.save.assert_awaited_once_with(folder)


@pytest.mark.asyncio
async def test_reorder_folders_requires_complete_unique_owned_list() -> None:
    owner_id = uuid4()
    first, second = FolderId(uuid4()), FolderId(uuid4())
    repository = AsyncMock(spec=IFolderRepository)
    repository.list_ids_by_owner.return_value = [first, second]
    use_case = ReorderFoldersUseCase(repository)

    await use_case.execute(ReorderFoldersCommand(owner_id, [second.value, first.value]))
    repository.set_order.assert_awaited_once_with(UserId(owner_id), [second, first])

    for invalid in ([first.value], [first.value, first.value], [first.value, uuid4()]):
        with pytest.raises(InvariantViolationError):
            await use_case.execute(ReorderFoldersCommand(owner_id, invalid))
    assert repository.set_order.await_count == 1
