from typing import Generic, Protocol, TypeVar

from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.interfaces.entity import Entity


ENTITY_contra = TypeVar("ENTITY_contra", bound=Entity, contravariant=True)


class IRepository(Protocol, Generic[ENTITY_contra]):
    async def add(self, entity: ENTITY_contra) -> None: ...
    async def save(self, entity: ENTITY_contra) -> None: ...


class EventBusRepository(Generic[ENTITY_contra]):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        repository: IRepository[ENTITY_contra],
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.repository = repository

    async def add(self, entity: ENTITY_contra) -> None:
        async with self.uow:
            await self.repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: ENTITY_contra) -> None:
        async with self.uow:
            await self.repository.save(entity)
            await self.event_bus.publish_all(entity.events)
