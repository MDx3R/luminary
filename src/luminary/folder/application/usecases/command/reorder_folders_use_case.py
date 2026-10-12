from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from common.domain.value_objects.order_key import order_key_between

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.reorder_folders_use_case import (
    IReorderFoldersUseCase,
    ReorderFoldersCommand,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId


class ReorderFoldersUseCase(IReorderFoldersUseCase):
    def __init__(
        self, repository: IFolderRepository, access_policy: IFolderAccessPolicy
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: ReorderFoldersCommand) -> None:
        folder = await self.repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)
        previous = await self._neighbour_key(folder, command.previous_folder_id)
        following = await self._neighbour_key(folder, command.next_folder_id)
        folder.change_order(order_key_between(previous, following))
        await self.repository.save(folder)

    async def _neighbour_key(
        self, folder: Folder, neighbour_id: UUID | None
    ) -> str | None:
        if neighbour_id is None:
            return None
        if neighbour_id == folder.id.value:
            raise InvariantViolationError("A folder cannot be its own order neighbour")
        neighbour = await self.repository.get_by_id(FolderId(neighbour_id))
        self.access_policy.assert_is_allowed(folder.owner_id, neighbour)
        return neighbour.order_key
