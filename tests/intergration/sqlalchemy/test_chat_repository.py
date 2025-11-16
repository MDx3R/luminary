from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload
from tests.unit.chat.utils import make_chat

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.domain.entity.folder import FolderId
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
class TestChatRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.chat_repository = ChatRepository(query_executor)

    async def _exists(self, chat_id: ChatId) -> bool:
        async with self.maker() as session:
            result = await session.get(ChatBase, chat_id.value)
            return result is not None

    async def _get(self, chat_id: ChatId) -> Chat | None:
        async with self.maker() as session:
            result = (
                (
                    await session.execute(
                        select(ChatBase)
                        .options(joinedload(ChatBase.sources))
                        .where(ChatBase.chat_id == chat_id.value)
                    )
                )
                .unique()
                .scalar_one_or_none()
            )
            if not result:
                return None
            return ChatMapper.to_domain(result)

    async def _add_chat(self, sources: list[SourceId] | None = None) -> Chat:
        chat = make_chat()
        if sources:
            for s in sources:
                chat.add_source(s)
        async with self.maker() as session:
            session.add(ChatMapper.to_persistence(chat))
            await session.commit()
        return chat

    async def test_add_and_get_chat_success(self):
        chat = await self._add_chat()
        result = await self.chat_repository.get_by_id(chat.id)
        assert result == chat

    async def test_get_chat_not_found(self):
        with pytest.raises(NotFoundError):
            await self.chat_repository.get_by_id(ChatId(uuid4()))

    async def test_add_sources_and_save(self):
        chat = await self._add_chat()
        source_id1 = SourceId(uuid4())
        source_id2 = SourceId(uuid4())
        chat.add_source(source_id1)
        chat.add_source(source_id2)

        await self.chat_repository.save(chat)

        updated = await self._get(chat.id)

        assert updated is not None
        assert set(updated.sources) == {source_id1, source_id2}

    async def test_save_removes_old_sources(self):
        chat = await self._add_chat([SourceId(uuid4()), SourceId(uuid4())])
        for source_id in list(chat.sources):
            chat.remove_source(source_id)
        new_source_id = SourceId(uuid4())
        chat.add_source(new_source_id)

        await self.chat_repository.save(chat)

        updated = await self._get(chat.id)

        assert updated is not None
        assert len(updated.sources) == 1
        assert new_source_id in updated.sources

    async def test_save_all_chats_sources(self):
        chat1 = await self._add_chat([SourceId(uuid4())])
        chat2 = await self._add_chat([SourceId(uuid4()), SourceId(uuid4())])

        for source_id in list(chat1.sources):
            chat1.remove_source(source_id)
        new_source_id1 = SourceId(uuid4())
        chat1.add_source(new_source_id1)

        for source_id in list(chat2.sources):
            chat2.remove_source(source_id)
        new_source_id2 = SourceId(uuid4())
        chat2.add_source(new_source_id2)

        await self.chat_repository.save_all([chat1, chat2])
        updated1 = await self._get(chat1.id)
        updated2 = await self._get(chat2.id)

        assert updated1 is not None
        assert updated2 is not None
        assert len(updated1.sources) == 1
        assert new_source_id1 in updated1.sources
        assert len(updated2.sources) == 1
        assert new_source_id2 in updated2.sources

    async def test_get_by_folder_id(self):
        folder_id = FolderId(uuid4())
        chat1 = make_chat(folder_id=folder_id.value, name="Chat1")
        chat2 = make_chat(folder_id=folder_id.value, name="Chat2")
        async with self.maker() as session:
            session.add(ChatMapper.to_persistence(chat1))
            session.add(ChatMapper.to_persistence(chat2))
            await session.commit()

        result = await self.chat_repository.get_by_folder_id(folder_id)
        assert {c.info.name for c in result} == {"Chat1", "Chat2"}
