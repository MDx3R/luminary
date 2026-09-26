from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.update_folder_info_use_case import (
    IUpdateFolderInfoUseCase,
    UpdateFolderInfoCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo


class UpdateFolderInfoUseCase(IUpdateFolderInfoUseCase):
    def __init__(
        self,
        repository: IFolderRepository,
        access_policy: IFolderAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateFolderInfoCommand) -> None:
        folder = await self.repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)

        new_info = FolderInfo(name=command.name, description=command.description)
        if folder.info_matches(new_info):
            return

        folder.change_info(new_info)
        await self.repository.save(folder)
