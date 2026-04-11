from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import add_folder
from tests.unit.folder.utils import make_folder

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
class TestFolderRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = FolderRepository(query_executor)

    async def test_get_by_id_success(self):
        # Arrange
        folder = await add_folder(self.maker)

        # Act
        result = await self.repository.get_by_id(folder.id)

        # Assert
        assert result.id == folder.id
        assert result.info.name == folder.info.name
        assert result.is_deleted is False

    async def test_get_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(FolderId(uuid4()))

    async def test_add_and_get(self):
        # Arrange
        folder = make_folder()

        # Act
        await self.repository.add(folder)
        loaded = await self.repository.get_by_id(folder.id)

        # Assert
        assert loaded.id == folder.id
        assert loaded.info.name == folder.info.name

    async def test_save_with_chats_and_sources(self):
        # Arrange
        folder = await add_folder(self.maker)
        chat_id = ChatId(uuid4())
        source_id = SourceId(uuid4())
        folder.add_chat(chat_id)
        folder.add_source(source_id)

        # Act
        await self.repository.save(folder)
        loaded = await self.repository.get_by_id(folder.id)

        # Assert
        assert {c.value for c in loaded.chats} == {chat_id.value}
        assert {s.value for s in loaded.sources} == {source_id.value}

    async def test_get_by_id_does_not_return_soft_deleted(self):
        # Arrange
        folder = await add_folder(self.maker)
        folder.delete()
        await self.repository.save(folder)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(folder.id)
