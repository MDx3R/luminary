from collections.abc import Sequence

from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class EventBusChatRepository(IChatRepository):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        repository: IChatRepository,
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def get_by_id(self, id: ChatId) -> Chat:
        return await self.repository.get_by_id(id)

    async def add(self, entity: Chat) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Chat) -> None:
        if not entity.has_changes():
            return
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)

    async def list_ids_by_location(
        self, owner_id: UserId, folder_id: FolderId | None
    ) -> Sequence[ChatId]:
        return await self.repository.list_ids_by_location(owner_id, folder_id)

    async def set_order(
        self, owner_id: UserId, folder_id: FolderId | None, chat_ids: Sequence[ChatId]
    ) -> None:
        async with self.uow:
            await self.repository.set_order(owner_id, folder_id, chat_ids)

    async def move_to_folder(self, chat_id: ChatId, folder_id: FolderId | None) -> None:
        async with self.uow:
            await self.repository.move_to_folder(chat_id, folder_id)

    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None:
        await self.repository.clear_assistant_reference(assistant_id)

    async def clear_source_reference(self, source_id: SourceId) -> None:
        await self.repository.clear_source_reference(source_id)

    async def clear_source_association(
        self, chat_id: ChatId, source_id: SourceId
    ) -> None:
        await self.repository.clear_source_association(chat_id, source_id)
