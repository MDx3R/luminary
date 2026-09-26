from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import joinedload

from luminary.assistant.domain.entity.assistant import AssistantId
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
    FolderChatAssociation,
    FolderSourceAssociation,
)
from luminary.source.domain.entity.source import SourceId


class FolderRepository(IFolderRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: FolderId) -> Folder:
        stmt = (
            select(FolderBase)
            .where(FolderBase.folder_id == id.value)
            .where(FolderBase.is_active)
            .options(
                joinedload(FolderBase.chat_associations),
                joinedload(FolderBase.source_associations),
            )
        )
        base = await self.executor.execute_scalar_one(stmt)
        if base is None:
            raise NotFoundError(id)

        return FolderMapper.to_domain(base)

    async def add(self, entity: Folder) -> None:
        base = FolderMapper.to_persistence(entity)
        await self.executor.add(base)

    async def save(self, entity: Folder) -> None:
        base = FolderMapper.to_persistence(entity)
        await self.executor.save(base)

    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None:
        stmt = (
            update(FolderBase)
            .where(FolderBase.assistant_id == assistant_id.value)
            .values(assistant_id=None)
        )
        await self.executor.execute(stmt)

    async def clear_source_reference(self, source_id: SourceId) -> None:
        stmt = delete(FolderSourceAssociation).where(
            FolderSourceAssociation.source_id == source_id.value
        )
        await self.executor.execute(stmt)

    async def clear_chat_association(
        self, folder_id: FolderId, chat_id: ChatId
    ) -> None:
        stmt = delete(FolderChatAssociation).where(
            and_(
                FolderChatAssociation.folder_id == folder_id.value,
                FolderChatAssociation.chat_id == chat_id.value,
            )
        )
        await self.executor.execute(stmt)

    async def clear_source_association(
        self, folder_id: FolderId, source_id: SourceId
    ) -> None:
        stmt = delete(FolderSourceAssociation).where(
            and_(
                FolderSourceAssociation.folder_id == folder_id.value,
                FolderSourceAssociation.source_id == source_id.value,
            )
        )
        await self.executor.execute(stmt)
