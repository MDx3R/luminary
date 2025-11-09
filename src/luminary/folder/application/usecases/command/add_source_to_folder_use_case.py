from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderCommand,
    IAddSourceToFolderUseCase,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import Source


class AddSourceToFolderUseCase(IAddSourceToFolderUseCase):
    def __init__(
        self,
        folder_access_policy: IFolderAccessPolicy,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
        source_access_policy: ISourceAccessPolicy,
        source_repository: ISourceRepository,
    ) -> None:
        self.folder_access_policy = folder_access_policy
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository
        self.source_access_policy = source_access_policy
        self.source_repository = source_repository

    async def execute(self, command: AddSourceToFolderCommand) -> None:
        folder = await self.folder_repository.get_by_id(command.folder_id)
        self.folder_access_policy.assert_is_allowed(command.user_id, folder)

        source = await self.source_repository.get_by_id(command.source_id)
        self.source_access_policy.assert_is_allowed(command.user_id, source)

        folder.add_source(command.source_id)

        await self.folder_repository.save(folder)

    async def add_source_to_chats(self, source: Source, folder: Folder) -> None:
        # TODO: Add tests
        chats = await self.chat_repository.get_by_folder_id(folder.folder_id)

        for ch in chats:
            ch.add_source(source.source_id)

        await self.chat_repository.save_all(chats)
