from common.application.interfaces.handlers.handler import IEventHandler
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.events.events import ChatMovedEvent
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)


class FolderChatMovedHandler(IEventHandler[ChatMovedEvent]):
    def __init__(
        self,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository
        self.uow = uow

    async def handle(self, event: ChatMovedEvent) -> None:
        async with self.uow:
            # Keep the chat lock until the projection is saved. Replayed events
            # use committed state, never their potentially stale destination.
            chat = await self.chat_repository.get_by_id_for_update(
                ChatId(event.chat_id)
            )
            if chat is None or chat.is_deleted:
                return
            await self.folder_repository.move_chat_association(chat.id, chat.folder_id)
