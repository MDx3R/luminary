from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.entity.assistant import Assistant, AssistantId


class EventBusAssistantRepository(IAssistantRepository):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        repository: IAssistantRepository,
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def get_by_id(self, id: AssistantId) -> Assistant:
        return await self.repository.get_by_id(id)

    async def add(self, entity: Assistant) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Assistant) -> None:
        if not entity.has_changes():
            return
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)
