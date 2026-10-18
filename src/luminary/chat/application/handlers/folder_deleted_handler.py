from common.application.interfaces.handlers.handler import IEventHandler
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.events.events import FolderDeletedEvent
from luminary.folder.domain.value_objects.folder_id import FolderId


class ChatFolderDeletedHandler(IEventHandler[FolderDeletedEvent]):
    def __init__(
        self,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository
        self.uow = uow

    async def handle(self, event: FolderDeletedEvent) -> None:
        async with self.uow:
            folder_id = FolderId(event.folder_id)
            # Wait for the producer's commit via the owning context's port.
            if await self.folder_repository.is_deleted_for_update(folder_id):
                # Preserve folder associations and all source records.
                await self.chat_repository.delete_by_folder(folder_id)
