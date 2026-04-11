from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class EventBusFolderRepository(IFolderRepository):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        repository: IFolderRepository,
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def get_by_id(self, id: FolderId) -> Folder:
        return await self.repository.get_by_id(id)

    async def add(self, entity: Folder) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Folder) -> None:
        if not entity.has_changes():
            return
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)

    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None:
        await self.repository.clear_assistant_reference(assistant_id)

    async def clear_source_reference(self, source_id: SourceId) -> None:
        await self.repository.clear_source_reference(source_id)

    async def clear_chat_association(
        self, folder_id: FolderId, chat_id: ChatId
    ) -> None:
        await self.repository.clear_chat_association(folder_id, chat_id)

    async def clear_source_association(
        self, folder_id: FolderId, source_id: SourceId
    ) -> None:
        await self.repository.clear_source_association(folder_id, source_id)
