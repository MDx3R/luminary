from collections.abc import Iterable, Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
    ChatSourceBase,
)


class ChatRepository(IChatRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, chat_id: UUID) -> Chat:
        stmt = (
            select(ChatBase)
            .where(ChatBase.chat_id == chat_id)
            .options(joinedload(ChatBase.sources))
        )

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(chat_id)
        return ChatMapper.to_domain(result)

    async def get_by_folder_id(self, folder_id: UUID) -> Sequence[Chat]:
        stmt = (
            select(ChatBase)
            .where(ChatBase.folder_id == folder_id)
            .options(joinedload(ChatBase.sources))
        )

        result = await self.executor.execute_scalar_many(stmt)
        return [ChatMapper.to_domain(i) for i in result]

    async def add(self, entity: Chat) -> None:
        model = ChatMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Chat) -> None:
        model = ChatMapper.to_persistence(entity)
        async with self.executor.uow:
            stmt = delete(ChatSourceBase).where(
                ChatSourceBase.chat_id == entity.chat_id
            )
            await self.executor.execute(stmt)

            await self.executor.add_all(model.sources)
            model.sources = []

            await self.executor.save(model)

    async def save_all(self, entities: Iterable[Chat]) -> None:
        models = [ChatMapper.to_persistence(e) for e in entities]
        async with self.executor.uow:
            chat_ids = [e.chat_id for e in entities]
            stmt = delete(ChatSourceBase).where(ChatSourceBase.chat_id.in_(chat_ids))
            await self.executor.execute(stmt)

            sources: list[ChatSourceBase] = []
            for m in models:
                sources.extend(m.sources)
                m.sources = []
            await self.executor.add_all(sources)

            await self.executor.save_all(models)
