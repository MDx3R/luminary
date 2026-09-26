from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import add_chat
from tests.unit.chat.utils import make_chat

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
class TestChatRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = ChatRepository(query_executor)

    async def test_get_by_id_success(self):
        # Arrange
        chat = await add_chat(self.maker)

        # Act
        result = await self.repository.get_by_id(chat.id)

        # Assert
        assert result.id == chat.id
        assert result.info.name == chat.info.name
        assert result.is_deleted is False

    async def test_get_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(ChatId(uuid4()))

    async def test_add_and_get(self):
        # Arrange
        chat = make_chat()

        # Act
        await self.repository.add(chat)
        loaded = await self.repository.get_by_id(chat.id)

        # Assert
        assert loaded.id == chat.id
        assert loaded.info.name == chat.info.name

    async def test_save_with_sources(self):
        # Arrange
        chat = await add_chat(self.maker)
        source_id = SourceId(uuid4())
        chat.add_source(source_id)

        # Act
        await self.repository.save(chat)
        loaded = await self.repository.get_by_id(chat.id)

        # Assert
        assert {s.value for s in loaded.sources} == {source_id.value}

    async def test_get_by_id_does_not_return_soft_deleted(self):
        # Arrange
        chat = await add_chat(self.maker)
        chat.delete()
        await self.repository.save(chat)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(chat.id)
