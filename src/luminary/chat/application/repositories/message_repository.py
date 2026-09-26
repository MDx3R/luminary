from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.value_objects.message_id import MessageId


class EventBusMessageRepository(IMessageRepository):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        repository: IMessageRepository,
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def get_by_id(self, id: MessageId) -> Message:
        return await self.repository.get_by_id(id)

    async def add(self, entity: Message) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Message) -> None:
        if not entity.has_changes():
            return
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)
