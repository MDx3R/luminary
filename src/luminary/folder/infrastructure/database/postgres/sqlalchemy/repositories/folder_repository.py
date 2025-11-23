from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder, FolderId
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import (
    FolderMapper,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatBase,
    FolderSourceBase,
)


class FolderRepository(IFolderRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: FolderId) -> Folder:
        stmt = (
            select(FolderBase)
            .where(FolderBase.folder_id == id.value)
            .options(joinedload(FolderBase.chats))
            .options(joinedload(FolderBase.sources))
        )

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(id)
        return FolderMapper.to_domain(result)

    async def add(self, entity: Folder) -> None:
        model = FolderMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Folder) -> None:
        # TODO: Remove this after refactor on entities for them to be eventual consistent
        model = FolderMapper.to_persistence(entity)
        async with self.executor.uow:
            stmt = delete(FolderChatBase).where(
                FolderChatBase.folder_id == entity.id.value
            )
            await self.executor.execute(stmt)
            stmt = delete(FolderSourceBase).where(
                FolderSourceBase.folder_id == entity.id.value
            )
            await self.executor.execute(stmt)

            await self.executor.add_all(model.chats)
            model.chats = []
            await self.executor.add_all(model.sources)
            model.sources = []

            await self.executor.save(model)
