from uuid import UUID

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
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
from luminary.folder.domain.entity.folder import Folder


class RemoveSourceFromFolderUseCase(IRemoveSourceFromFolderUseCase):
    def __init__(
        self,
        folder_access_policy: IFolderAccessPolicy,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
    ) -> None:
        self.folder_access_policy = folder_access_policy
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository

    async def execute(self, command: RemoveSourceFromFolderCommand) -> None:
        folder = await self.folder_repository.get_by_id(command.folder_id)
        self.folder_access_policy.assert_is_allowed(command.user_id, folder)

        if not folder.has_source(command.source_id):
            return

        folder.remove_source(command.source_id)
        await self.folder_repository.save(folder)

    async def remove_source_from_chats(self, source_id: UUID, folder: Folder) -> None:
        # TODO: Add tests
        # TODO: Eventual consistency
        chats = await self.chat_repository.get_by_folder_id(folder.folder_id)

        for ch in chats:
            ch.remove_source(source_id)

        await self.chat_repository.save_all(chats)
