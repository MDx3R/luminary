from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.remove_folder_assistant_use_case import (
    IRemoveFolderAssistantUseCase,
    RemoveFolderAssistantCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class RemoveFolderAssistantUseCase(IRemoveFolderAssistantUseCase):
    def __init__(
        self,
        repository: IFolderRepository,
        access_policy: IFolderAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: RemoveFolderAssistantCommand) -> None:
        folder = await self.repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)

        if folder.assistant_matches(None):
            return

        folder.remove_assistant()
        await self.repository.save(folder)
