from collections.abc import Sequence

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.chat.application.interfaces.repositories.message_reader import (
    IMessageReader,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.message_mapper import (
    MessageMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.message_base import (
    MessageBase,
)


class MessageRepository(IMessageRepository, IMessageReader):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_chat_messages(
        self, chat_id: ChatId, *, limit: int | None = None
    ) -> Sequence[Message]:
        stmt = (
            select(MessageBase)
            .where(MessageBase.chat_id == chat_id.value)
            .order_by(MessageBase.created_at.desc())
        )

        stmt = stmt.limit(limit)

        result = await self.executor.execute_scalar_many(stmt)
        domain = [MessageMapper.to_domain(b) for b in reversed(result)]
        return domain

    async def get_by_id(self, id: MessageId) -> Message:
        stmt = select(MessageBase).where(MessageBase.message_id == id.value)

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(id)

        return MessageMapper.to_domain(result)

    async def add(self, entity: Message) -> None:
        base = MessageMapper.to_persistence(entity)
        await self.executor.add(base)

    async def save(self, entity: Message) -> None:
        base = MessageMapper.to_persistence(entity)
        await self.executor.save(base)
