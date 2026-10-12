from common.application.exceptions import NotFoundError
from common.application.interfaces.handlers.handler import IEventHandler

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.events.events import ChatDeletedEvent
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.events.events import FolderChatRemovedEvent
from luminary.folder.domain.value_objects.folder_id import FolderId


class FolderChatDeletedHandler(IEventHandler[ChatDeletedEvent]):
    """Delete chat from folder when an chat is soft-deleted."""

    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: ChatDeletedEvent) -> None:
        if not event.folder_id:
            return

        try:
            folder = await self.folder_repository.get_by_id(FolderId(event.folder_id))
        except NotFoundError:
            return

        chat_id = ChatId(event.chat_id)
        if not folder.has_chat(chat_id):
            return

        folder.remove_chat(chat_id)
        await self.folder_repository.save(folder)


class FolderChatRemovedHandler(IEventHandler[FolderChatRemovedEvent]):
    """Delete the chat and clear its association in a single event handler."""

    def __init__(
        self, chat_repository: IChatRepository, folder_repository: IFolderRepository
    ) -> None:
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository

    async def handle(self, event: FolderChatRemovedEvent) -> None:
        await self._delete_chat(event)
        await self.folder_repository.clear_chat_association(
            FolderId(event.folder_id), ChatId(event.chat_id)
        )

    async def _delete_chat(self, event: FolderChatRemovedEvent) -> None:
        try:
            chat = await self.chat_repository.get_by_id(ChatId(event.chat_id))
        except NotFoundError:
            return

        if chat.is_deleted or chat.folder_id != FolderId(event.folder_id):
            return

        chat.delete()
        await self.chat_repository.save(chat)
