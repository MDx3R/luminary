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

        folder = await self.folder_repository.get_by_id(FolderId(event.folder_id))

        chat_id = ChatId(event.chat_id)
        if not folder.has_chat(chat_id):
            return

        folder.remove_chat(chat_id)
        await self.folder_repository.save(folder)


class FolderChatRemovedAssociationHandler(IEventHandler[FolderChatRemovedEvent]):
    """Remove chat association when folder chat is removed from folder."""

    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: FolderChatRemovedEvent) -> None:
        await self.folder_repository.clear_chat_association(
            FolderId(event.folder_id), ChatId(event.chat_id)
        )


class FolderChatRemovedHandler(IEventHandler[FolderChatRemovedEvent]):
    """Delete chat when an folder chat is removed from folder."""

    def __init__(self, chat_repository: IChatRepository) -> None:
        self.chat_repository = chat_repository

    async def handle(self, event: FolderChatRemovedEvent) -> None:
        chat = await self.chat_repository.get_by_id(ChatId(event.chat_id))

        if chat.is_deleted:
            return

        chat.delete()
        await self.chat_repository.save(chat)
