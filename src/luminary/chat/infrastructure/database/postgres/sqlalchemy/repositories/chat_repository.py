from collections.abc import Sequence

from common.application.exceptions import NotFoundError
from common.domain.value_objects.id import UserId
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import joinedload

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
    ChatSourceAssociation,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderChatAssociation,
)
from luminary.source.domain.entity.source import SourceId


class ChatRepository(IChatRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: ChatId) -> Chat:
        stmt = (
            select(ChatBase)
            .where(ChatBase.chat_id == id.value)
            .where(ChatBase.is_active)
            .options(joinedload(ChatBase.source_associations))
        )
        base = await self.executor.execute_scalar_one(stmt)
        if base is None:
            raise NotFoundError(id)

        return ChatMapper.to_domain(base)

    async def add(self, entity: Chat) -> None:
        base = ChatMapper.to_persistence(entity)
        await self.executor.add(base)

    async def save(self, entity: Chat) -> None:
        base = ChatMapper.to_persistence(entity)
        await self.executor.save(base)

    async def list_ids_by_location(
        self, owner_id: UserId, folder_id: FolderId | None
    ) -> Sequence[ChatId]:
        stmt = select(ChatBase.chat_id).where(
            ChatBase.owner_id == owner_id.value, ChatBase.is_active
        )
        if folder_id is None:
            stmt = stmt.where(ChatBase.folder_id.is_(None))
        else:
            stmt = stmt.where(ChatBase.folder_id == folder_id.value)
        ids = await self.executor.execute_scalar_many(stmt)
        return [ChatId(id) for id in ids]

    async def set_order(
        self, owner_id: UserId, folder_id: FolderId | None, chat_ids: Sequence[ChatId]
    ) -> None:
        for position, chat_id in enumerate(chat_ids):
            stmt = update(ChatBase).where(
                ChatBase.chat_id == chat_id.value,
                ChatBase.owner_id == owner_id.value,
                ChatBase.is_active,
            )
            if folder_id is None:
                stmt = stmt.where(ChatBase.folder_id.is_(None))
            else:
                stmt = stmt.where(ChatBase.folder_id == folder_id.value)
            await self.executor.execute(stmt.values(sort_order=position))

    async def move_to_folder(self, chat_id: ChatId, folder_id: FolderId | None) -> None:
        await self.executor.execute(
            delete(FolderChatAssociation).where(
                FolderChatAssociation.chat_id == chat_id.value
            )
        )
        await self.executor.execute(
            update(ChatBase)
            .where(ChatBase.chat_id == chat_id.value, ChatBase.is_active)
            .values(folder_id=folder_id.value if folder_id else None, sort_order=-1)
        )
        if folder_id is not None:
            await self.executor.add(
                FolderChatAssociation(folder_id=folder_id.value, chat_id=chat_id.value)
            )

    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None:
        stmt = (
            update(ChatBase)
            .where(ChatBase.assistant_id == assistant_id.value)
            .values(assistant_id=None)
        )
        await self.executor.execute(stmt)

    async def clear_source_reference(self, source_id: SourceId) -> None:
        stmt = delete(ChatSourceAssociation).where(
            ChatSourceAssociation.source_id == source_id.value
        )
        await self.executor.execute(stmt)

    async def clear_source_association(
        self, chat_id: ChatId, source_id: SourceId
    ) -> None:
        stmt = delete(ChatSourceAssociation).where(
            and_(
                ChatSourceAssociation.chat_id == chat_id.value,
                ChatSourceAssociation.source_id == source_id.value,
            )
        )
        await self.executor.execute(stmt)
