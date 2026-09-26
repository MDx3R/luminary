"""Read repository implementation for Chat: ORM -> read models (cross-BC)."""

from collections.abc import Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload, with_polymorphic

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.chat.application.dtos.read_models import (
    ChatReadModel,
    ChatSummaryReadModel,
    MessageReadModel,
)
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatReadMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.message_mapper import (
    MessageReadMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.message_base import (
    MessageBase,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class ChatReadRepository(IChatReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self._executor = executor

    async def get_by_id(self, chat_id: UUID, owner_id: UUID) -> ChatReadModel:
        sources = with_polymorphic(SourceBase, "*", aliased=True)

        stmt = (
            select(ChatBase)
            .where(ChatBase.chat_id == chat_id)
            .where(ChatBase.owner_id == owner_id)
            .where(ChatBase.is_active)
            .options(joinedload(ChatBase.assistant).load_only(AssistantBase.name))
            .options(joinedload(ChatBase.sources.of_type(sources)))
        )
        result = await self._executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(str(chat_id))

        return ChatReadMapper.to_read(result)

    async def list_standalone_by_owner(
        self, owner_id: UUID
    ) -> Sequence[ChatSummaryReadModel]:
        stmt = (
            select(ChatBase)
            .where(ChatBase.owner_id == owner_id)
            .where(ChatBase.folder_id.is_(None))
            .where(ChatBase.is_active)
            .order_by(ChatBase.created_at.desc())
        )
        result = await self._executor.execute_scalar_many(stmt)
        return [ChatReadMapper.to_summary(c) for c in result]

    async def list_messages(
        self,
        chat_id: UUID,
        owner_id: UUID,
        *,
        limit: int = 50,
        before: UUID | None = None,
    ) -> Sequence[MessageReadModel]:
        before_subq = (
            select(MessageBase.created_at)
            .where(MessageBase.message_id == before)
            .scalar_subquery()
        )
        stmt = (
            select(MessageBase)
            .join(ChatBase, MessageBase.chat_id == ChatBase.chat_id)
            .where(
                and_(
                    ChatBase.chat_id == chat_id,
                    ChatBase.owner_id == owner_id,
                    ChatBase.is_active,
                ),
            )
            .order_by(MessageBase.created_at.desc())
            .limit(limit)
            .options(joinedload(MessageBase.attachments))
        )

        if before is not None:
            stmt = stmt.where(MessageBase.created_at < before_subq)

        result = await self._executor.execute_scalar_many(stmt)

        return [MessageReadMapper.to_read(m) for m in result]
