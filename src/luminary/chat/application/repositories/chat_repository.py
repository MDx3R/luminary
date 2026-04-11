from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
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

    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None:
        await self.repository.clear_assistant_reference(assistant_id)

    async def clear_source_reference(self, source_id: SourceId) -> None:
        await self.repository.clear_source_reference(source_id)

    async def clear_source_association(
        self, chat_id: ChatId, source_id: SourceId
    ) -> None:
        await self.repository.clear_source_association(chat_id, source_id)
