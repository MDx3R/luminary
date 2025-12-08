from common.application.interfaces.services.event_bus import IEventBus
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder


class EventBusFolderRepository(IFolderRepository):
    def __init__(
        self,
        uow: IUnitOfWork,
        event_bus: IEventBus,
        folder_repository: IFolderRepository,
    ) -> None:
        self.uow = uow
        self.event_bus = event_bus
        self.folder_repository = folder_repository

    async def add(self, entity: Folder) -> None:
        async with self.uow:
            await self.folder_repository.add(entity)
            await self.event_bus.publish_all(entity.events)

    async def save(self, entity: Folder) -> None:
        async with self.uow:
            await self.folder_repository.save(entity)
            await self.event_bus.publish_all(entity.events)
