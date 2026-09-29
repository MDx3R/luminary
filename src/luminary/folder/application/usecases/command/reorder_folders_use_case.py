from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.reorder_folders_use_case import (
    IReorderFoldersUseCase,
    ReorderFoldersCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class ReorderFoldersUseCase(IReorderFoldersUseCase):
    def __init__(self, repository: IFolderRepository) -> None:
        self.repository = repository

    async def execute(self, command: ReorderFoldersCommand) -> None:
        owner_id = UserId(command.user_id)
        requested = [FolderId(id) for id in command.folder_ids]
        current = await self.repository.list_ids_by_owner(owner_id)
        if len(requested) != len(current) or set(requested) != set(current):
            raise InvariantViolationError(
                "folder_ids must contain every active folder owned by the user exactly once"
            )
        await self.repository.set_order(owner_id, requested)
