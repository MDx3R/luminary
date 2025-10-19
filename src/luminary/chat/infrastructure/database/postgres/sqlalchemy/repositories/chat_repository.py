from collections.abc import Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)


class ChatRepository(IChatRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, chat_id: UUID) -> Chat:
        stmt = select(ChatBase).where(ChatBase.chat_id == chat_id)

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(chat_id)
        return ChatMapper.to_domain(result)

    async def get_by_folder_id(self, folder_id: UUID) -> Sequence[Chat]:
        stmt = select(ChatBase).where(ChatBase.folder_id == folder_id)

        result = await self.executor.execute_scalar_many(stmt)
        return [ChatMapper.to_domain(i) for i in result]

    async def add(self, entity: Chat) -> None:
        model = ChatMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Chat) -> None:
        model = ChatMapper.to_persistence(entity)
        await self.executor.save(model)
