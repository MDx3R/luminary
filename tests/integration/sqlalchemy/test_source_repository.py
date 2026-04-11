from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import (
    add_file_source,
    add_link_source,
    add_page_source,
)
from tests.unit.source.utils import make_file_source, make_link_source, make_page_source

from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import SourceId
from luminary.source.infrastructure.database.postgres.sqlalchemy.repositories.source_repository import (
    SourceRepository,
)


@pytest.mark.asyncio
class TestSourceRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = SourceRepository(query_executor)

    async def test_get_file_source_success(self):
        # Arrange
        source = await add_file_source(self.maker)

        # Act
        result = await self.repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_link_source_success(self):
        # Arrange
        source = await add_link_source(self.maker)

        # Act
        result = await self.repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_page_source_success(self):
        # Arrange
        source = await add_page_source(self.maker)

        # Act
        result = await self.repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_source_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(SourceId(uuid4()))

    async def test_add_file_source_success(self):
        # Arrange
        source = make_file_source()

        # Act
        await self.repository.add(source)

        # Assert
        saved_source = await self.repository.get_by_id(source.id)
        assert saved_source == source

    async def test_add_link_source_success(self):
        # Arrange
        source = make_link_source()

        # Act
        await self.repository.add(source)

        # Assert
        saved_source = await self.repository.get_by_id(source.id)
        assert saved_source == source

    async def test_add_page_source_success(self):
        # Arrange
        source = make_page_source()

        # Act
        await self.repository.add(source)

        # Assert
        saved_source = await self.repository.get_by_id(source.id)
        assert saved_source == source

    async def test_save_file_source_success(self):
        # Arrange
        source = await add_file_source(self.maker)
        source.title = Title("New File Source 123")

        # Act
        await self.repository.save(source)

        # Assert
        updated_source = await self.repository.get_by_id(source.id)
        assert updated_source is not None
        assert updated_source.title == source.title

    async def test_save_link_source_success(self):
        # Arrange
        source = await add_link_source(self.maker)
        source.url = Url("https://updated-example.com")

        # Act
        await self.repository.save(source)

        # Assert
        updated_source = await self.repository.get_by_id(source.id)
        assert isinstance(updated_source, LinkSource)
        assert updated_source is not None
        assert updated_source.url == Url("https://updated-example.com")

    async def test_save_page_source_success(self):
        # Arrange
        source = await add_page_source(self.maker)
        source.editable = False

        # Act
        await self.repository.save(source)

        # Assert
        updated_source = await self.repository.get_by_id(source.id)
        assert isinstance(updated_source, PageSource)
        assert updated_source is not None
        assert updated_source.editable is False
