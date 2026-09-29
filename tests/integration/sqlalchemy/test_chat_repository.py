from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import (
    add_chat,
    add_file_source,
    add_folder,
    persist_chat,
)
from tests.unit.chat.utils import make_chat

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_read_repository import (
    FolderReadRepository,
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

    async def test_move_to_folder_and_root_preserves_chat_sources(
        self, query_executor: QueryExecutor
    ):
        owner_id = uuid4()
        source = await add_file_source(self.maker, owner_id=owner_id)
        chat = make_chat(user_id=owner_id)
        chat.add_source(source.id)
        await persist_chat(self.maker, chat)
        folder = await add_folder(self.maker, owner_id=owner_id)

        await self.repository.move_to_folder(chat.id, folder.id)

        moved = await self.repository.get_by_id(chat.id)
        assert moved.folder_id == folder.id
        assert source.id in moved.sources
        detail = await FolderReadRepository(query_executor).get_by_id(
            folder.id.value, owner_id
        )
        assert [item.id for item in detail.chats] == [chat.id.value]

        await self.repository.move_to_folder(chat.id, None)

        assert (await self.repository.get_by_id(chat.id)).folder_id is None
        detail = await FolderReadRepository(query_executor).get_by_id(
            folder.id.value, owner_id
        )
        assert detail.chats == []
        assert source.id in (await self.repository.get_by_id(chat.id)).sources

    async def test_set_order_scopes_to_location(self):
        owner_id = uuid4()
        first = await add_chat(self.maker, user_id=owner_id)
        second = await add_chat(self.maker, user_id=owner_id)
        folder = await add_folder(self.maker, owner_id=owner_id)
        other = await add_chat(self.maker, user_id=owner_id, folder_id=folder.id.value)

        await self.repository.set_order(
            first.owner_id, None, [second.id, first.id, other.id]
        )

        assert (await self.repository.get_by_id(second.id)).sort_order == 0
        assert (await self.repository.get_by_id(first.id)).sort_order == 1
        assert (await self.repository.get_by_id(other.id)).sort_order == -1
