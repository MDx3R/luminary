from common.application.interfaces.handlers.handler import IEventHandler
from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.events.chat_events import ChatAddSourceRequestedEvent
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.events.events import (
    FolderSourceAddedEvent,
    FolderSourceRemovedEvent,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class FolderSourceAddedHandler(IEventHandler[FolderSourceAddedEvent]):
    def __init__(
        self,
        folder_repository: IFolderRepository,
        event_bus: IEventBus,
    ) -> None:
        self.folder_repository = folder_repository
        self.event_bus = event_bus

    async def handle(self, event: FolderSourceAddedEvent) -> None:
        folder = await self.folder_repository.get_by_id(FolderId(event.folder_id))
        events = [
            ChatAddSourceRequestedEvent(chat_id=c.value, source_id=event.source_id)
            for c in folder.chats
        ]
        # TODO: Potentially we should add source to folder here
        await self.event_bus.publish_all(events)


class FolderSourceRemovedHandler(IEventHandler[FolderSourceRemovedEvent]):
    def __init__(
        self,
        uow: IUnitOfWork,
        folder_repository: IFolderRepository,
        event_bus: IEventBus,
    ) -> None:
        self.uow = uow
        self.folder_repository = folder_repository
        self.event_bus = event_bus

    async def handle(self, event: FolderSourceRemovedEvent) -> None:
        folder_id = FolderId(event.folder_id)
        folder = await self.folder_repository.get_by_id(folder_id)
        events = [
            ChatAddSourceRequestedEvent(chat_id=c.value, source_id=event.source_id)
            for c in folder.chats
        ]

        async with self.uow:
            await self.folder_repository.remove_source(
                folder_id, SourceId(event.source_id)
            )
            await self.event_bus.publish_all(events)
