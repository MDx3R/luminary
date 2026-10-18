from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import and_, delete, literal, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.events.events import (
    FolderChatAddedEvent,
    FolderChatRemovedEvent,
    FolderSourceAddedEvent,
    FolderSourceRemovedEvent,
)
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
        # Never merge a stale snapshot of the aggregate's associations.
        async with self.executor.uow:
            values = FolderMapper.to_update_values(entity)
            if values:
                await self.executor.execute(
                    update(FolderBase)
                    .where(FolderBase.folder_id == entity.id.value)
                    .values(**values)
                )
            await self._save_chat_changes(entity)
            await self._save_source_changes(entity)

    async def _save_chat_changes(self, entity: Folder) -> None:
        for event in entity.events:
            if isinstance(event, FolderChatAddedEvent):
                await self.executor.execute(
                    insert(FolderChatAssociation)
                    .values(folder_id=entity.id.value, chat_id=event.chat_id)
                    .on_conflict_do_nothing()
                )
            elif isinstance(event, FolderChatRemovedEvent):
                await self.clear_chat_association(entity.id, ChatId(event.chat_id))

    async def _save_source_changes(self, entity: Folder) -> None:
        for event in entity.events:
            if isinstance(event, FolderSourceAddedEvent):
                await self.executor.execute(
                    insert(FolderSourceAssociation)
                    .values(folder_id=entity.id.value, source_id=event.source_id)
                    .on_conflict_do_nothing()
                )
            elif isinstance(event, FolderSourceRemovedEvent):
                await self.clear_source_association(
                    entity.id, SourceId(event.source_id)
                )

    async def is_deleted_for_update(self, id: FolderId) -> bool:
        return (
            await self.executor.execute_scalar_one(
                select(FolderBase.is_deleted)
                .where(FolderBase.folder_id == id.value)
                .with_for_update()
            )
        ) is True

    async def move_chat_association(
        self, chat_id: ChatId, folder_id: FolderId | None
    ) -> None:
        async with self.executor.uow:
            await self._replace_chat_association(chat_id, folder_id)

    async def _replace_chat_association(
        self, chat_id: ChatId, folder_id: FolderId | None
    ) -> None:
        if folder_id is not None:
            is_deleted = await self.executor.execute_scalar_one(
                select(FolderBase.is_deleted).where(
                    FolderBase.folder_id == folder_id.value
                )
            )
            # A delayed move may arrive before the folder deletion has reached
            # its chats. Keep the soft-deleted folder's associations in that case.
            if is_deleted is not False:
                return
        await self.executor.execute(
            delete(FolderChatAssociation).where(
                FolderChatAssociation.chat_id == chat_id.value
            )
        )
        if folder_id is not None:
            await self.executor.execute(
                insert(FolderChatAssociation)
                .from_select(
                    ["folder_id", "chat_id"],
                    select(FolderBase.folder_id, literal(chat_id.value)).where(
                        FolderBase.folder_id == folder_id.value, FolderBase.is_active
                    ),
                )
                .on_conflict_do_nothing()
            )

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
                select(FolderBase.folder_id)
                .where(FolderBase.folder_id == folder_id.value, FolderBase.is_active)
                .exists(),
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
