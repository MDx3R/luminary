from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId

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
from luminary.folder.domain.entity.folder import Folder, FolderId
from luminary.source.domain.entity.source import SourceId


class RemoveSourceFromFolderUseCase(IRemoveSourceFromFolderUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        folder_access_policy: IFolderAccessPolicy,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
    ) -> None:
        self.uow = uow
        self.folder_access_policy = folder_access_policy
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository

    async def execute(self, command: RemoveSourceFromFolderCommand) -> None:
        source_id = SourceId(command.source_id)

        folder = await self.folder_repository.get_by_id(FolderId(command.folder_id))
        self.folder_access_policy.assert_is_allowed(UserId(command.user_id), folder)

        if not folder.has_source(source_id):
            return

        folder.remove_source(source_id)

        async with self.uow:
            await self.folder_repository.save(folder)
            await self.remove_source_from_chats(source_id, folder)

    async def remove_source_from_chats(
        self, source_id: SourceId, folder: Folder
    ) -> None:
        # TODO: Add tests
        # TODO: Eventual consistency
        chats = await self.chat_repository.get_by_folder_id(folder.id)

        for ch in chats:
            ch.remove_source(source_id)

        await self.chat_repository.save_all(chats)
