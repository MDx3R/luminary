from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import (
    FolderMapper,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatBase,
    FolderSourceBase,
)
from luminary.source.domain.entity.source import SourceId


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
        model = FolderMapper.to_persistence(entity)
        async with self.executor.uow:
            await self.executor.save(model)

    async def remove_chat(self, folder_id: FolderId, chat_id: ChatId) -> None:
        stmt = delete(FolderChatBase).where(
            FolderChatBase.folder_id == folder_id.value,
            FolderChatBase.chat_id == chat_id.value,
        )
        await self.executor.execute(stmt)

    async def remove_source(self, folder_id: FolderId, source_id: SourceId) -> None:
        stmt = delete(FolderSourceBase).where(
            FolderSourceBase.folder_id == folder_id.value,
            FolderSourceBase.source_id == source_id.value,
        )
        await self.executor.execute(stmt)
