from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import and_, delete, literal, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
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

    async def move_chat_association(self, chat_id: ChatId) -> None:
        async with self.executor.uow:
            # Wait for the producing transaction; replay the committed state, not
            # the event's potentially stale destination. Serialize concurrent events.
            chat = await self.executor.execute_scalar_one(
                select(ChatBase)
                .where(ChatBase.chat_id == chat_id.value)
                .with_for_update()
            )
            if chat is None or chat.is_deleted:
                return
            await self._replace_chat_association(chat_id, chat.folder_id)

    async def _replace_chat_association(
        self, chat_id: ChatId, folder_id: UUID | None
    ) -> None:
        if folder_id is not None:
            is_deleted = await self.executor.execute_scalar_one(
                select(FolderBase.is_deleted).where(FolderBase.folder_id == folder_id)
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
                        FolderBase.folder_id == folder_id, FolderBase.is_active
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
