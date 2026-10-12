from common.application.interfaces.handlers.handler import IEventHandler

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.folder.domain.events.events import FolderDeletedEvent
from luminary.folder.domain.value_objects.folder_id import FolderId


class ChatFolderDeletedHandler(IEventHandler[FolderDeletedEvent]):
    def __init__(self, chat_repository: IChatRepository) -> None:
        self.chat_repository = chat_repository

    async def handle(self, event: FolderDeletedEvent) -> None:
        # Preserve the deleted folder's associations and all source records.
        await self.chat_repository.delete_by_folder(FolderId(event.folder_id))
