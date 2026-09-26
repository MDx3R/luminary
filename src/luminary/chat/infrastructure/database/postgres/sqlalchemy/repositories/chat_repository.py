from common.application.exceptions import NotFoundError
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
