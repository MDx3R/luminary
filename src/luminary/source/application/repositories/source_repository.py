from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import Source, SourceId


class EventBusSourceRepository(ISourceRepository):
    def __init__(
        self, uow: IUnitOfWork, event_bus: IEventBus, repository: ISourceRepository
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def get_by_id(self, id: SourceId) -> Source:
        return await self.repository.get_by_id(id)

    async def add(self, entity: Source) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Source) -> None:
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)
