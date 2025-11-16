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
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderCommand,
    IAddSourceToFolderUseCase,
)
from luminary.folder.domain.entity.folder import Folder, FolderId
from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import Source, SourceId


class AddSourceToFolderUseCase(IAddSourceToFolderUseCase):
    def __init__(  # noqa: PLR0913
        self,
        uow: IUnitOfWork,
        folder_access_policy: IFolderAccessPolicy,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
        source_access_policy: ISourceAccessPolicy,
        source_repository: ISourceRepository,
    ) -> None:
        self.uow = uow
        self.folder_access_policy = folder_access_policy
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository
        self.source_access_policy = source_access_policy
        self.source_repository = source_repository

    async def execute(self, command: AddSourceToFolderCommand) -> None:
        user_id = UserId(command.user_id)
        source_id = SourceId(command.source_id)

        folder = await self.folder_repository.get_by_id(FolderId(command.folder_id))
        self.folder_access_policy.assert_is_allowed(user_id, folder)

        if folder.has_source(source_id):
            return

        source = await self.source_repository.get_by_id(source_id)
        self.source_access_policy.assert_is_allowed(user_id, source)

        folder.add_source(source_id)

        async with self.uow:
            await self.folder_repository.save(folder)
            await self.add_source_to_chats(source, folder)

    async def add_source_to_chats(self, source: Source, folder: Folder) -> None:
        # TODO: Add tests
        # TODO: Eventual consistency
        chats = await self.chat_repository.get_by_folder_id(folder.id)

        for ch in chats:
            ch.add_source(source.id)

        await self.chat_repository.save_all(chats)
