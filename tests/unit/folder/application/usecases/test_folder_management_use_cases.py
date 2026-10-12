from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
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
from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy
from luminary.folder.application.usecases.command.reorder_folders_use_case import (
    ReorderFoldersUseCase,
)
from luminary.folder.application.usecases.command.set_folder_collapsed_use_case import (
    SetFolderCollapsedUseCase,
)


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
@pytest.mark.parametrize("placement", ["start", "middle", "end"])
async def test_reorder_folders_saves_only_moved_folder(placement) -> None:
    owner_id = uuid4()
    first = make_folder(owner_id=owner_id)
    second = make_folder(owner_id=owner_id)
    moved = make_folder(owner_id=owner_id)
    first.change_order("a0")
    second.change_order("a1")
    repository = AsyncMock(spec=IFolderRepository)
    folders = {folder.id: folder for folder in (first, second, moved)}
    repository.get_by_id.side_effect = folders.__getitem__
    use_case = ReorderFoldersUseCase(repository, FolderAccessPolicy())
    previous = first if placement != "start" else None
    following = second if placement != "end" else None
    await use_case.execute(
        ReorderFoldersCommand(
            owner_id,
            moved.id.value,
            previous.id.value if previous else None,
            following.id.value if following else None,
        )
    )
    repository.save.assert_awaited_once_with(moved)
    assert first.order_key == "a0"
    assert second.order_key == "a1"
    assert previous is None or previous.order_key < moved.order_key
    assert following is None or moved.order_key < following.order_key


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid", ["self", "duplicate", "reversed", "other-owner", "missing"]
)
async def test_reorder_folders_rejects_invalid_neighbours(invalid) -> None:
    owner_id = uuid4()
    moved = make_folder(owner_id=owner_id)
    previous = make_folder(owner_id=owner_id)
    following = make_folder(owner_id=owner_id)
    previous.change_order("a0")
    following.change_order("a1")
    previous_id, next_id = previous.id.value, following.id.value
    if invalid == "self":
        previous_id = moved.id.value
    elif invalid == "duplicate":
        next_id = previous_id
    elif invalid == "reversed":
        previous_id, next_id = next_id, previous_id
    elif invalid == "other-owner":
        previous.owner_id = UserId(uuid4())
    repository = AsyncMock(spec=IFolderRepository)
    folders = {folder.id: folder for folder in (moved, previous, following)}
    repository.get_by_id.side_effect = folders.__getitem__
    if invalid == "missing":
        repository.get_by_id.side_effect = [moved, NotFoundError(previous.id)]
    use_case = ReorderFoldersUseCase(repository, FolderAccessPolicy())
    with pytest.raises((InvariantViolationError, AccessPolicyError, NotFoundError)):
        await use_case.execute(
            ReorderFoldersCommand(owner_id, moved.id.value, previous_id, next_id)
        )
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_reorder_folder_rejects_inaccessible_folder() -> None:
    folder = make_folder()
    repository = AsyncMock(spec=IFolderRepository)
    repository.get_by_id.return_value = folder
    use_case = ReorderFoldersUseCase(repository, FolderAccessPolicy())
    with pytest.raises(AccessPolicyError):
        await use_case.execute(ReorderFoldersCommand(uuid4(), folder.id.value))
    repository.save.assert_not_awaited()
