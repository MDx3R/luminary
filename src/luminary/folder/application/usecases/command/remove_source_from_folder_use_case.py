from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    IRemoveSourceFromFolderUseCase,
    RemoveSourceFromFolderCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class RemoveSourceFromFolderUseCase(IRemoveSourceFromFolderUseCase):
    def __init__(
        self,
        folder_access_policy: IFolderAccessPolicy,
        folder_repository: IFolderRepository,
    ) -> None:
        self.folder_access_policy = folder_access_policy
        self.folder_repository = folder_repository

    async def execute(self, command: RemoveSourceFromFolderCommand) -> None:
        source_id = SourceId(command.source_id)

        folder = await self.folder_repository.get_by_id(FolderId(command.folder_id))
        self.folder_access_policy.assert_is_allowed(UserId(command.user_id), folder)

        if not folder.has_source(source_id):
            return

        folder.remove_source(source_id)

        await self.folder_repository.save(folder)
