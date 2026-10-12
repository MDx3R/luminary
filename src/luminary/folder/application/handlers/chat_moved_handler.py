from common.application.interfaces.handlers.handler import IEventHandler

from luminary.chat.domain.events.events import ChatMovedEvent
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)


class FolderChatMovedHandler(IEventHandler[ChatMovedEvent]):
    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: ChatMovedEvent) -> None:
        # Replayed/out-of-order events must reflect the current chat location.
        await self.folder_repository.move_chat_association(ChatId(event.chat_id))
