from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.unit.source.utils import make_file_source, make_link_source, make_page_source

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import SourceId
from luminary.source.infrastructure.database.postgres.sqlalchemy.mappers.source_mapper import (
    SourceMapper,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    FileSourceBase,
    LinkSourceBase,
    PageSourceBase,
)
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
        self.source_repository = SourceRepository(query_executor)

    async def _exists(self, source_id: SourceId) -> bool:
        async with self.maker() as session:
            result = await session.get(FileSourceBase, source_id.value)
            if result:
                return True
            result = await session.get(LinkSourceBase, source_id.value)  # type: ignore[arg-type]
            if result:
                return True
            result = await session.get(PageSourceBase, source_id.value)  # type: ignore[arg-type]
            return result is not None

    async def _get_file_source(self, source_id: SourceId) -> FileSource | None:
        async with self.maker() as session:
            result = await session.get(FileSourceBase, source_id.value)
            if not result:
                return None
            source = SourceMapper.to_domain(result)
            assert isinstance(source, FileSource)
            return source

    async def _get_link_source(self, source_id: SourceId) -> LinkSource | None:
        async with self.maker() as session:
            result = await session.get(LinkSourceBase, source_id.value)
            if not result:
                return None
            source = SourceMapper.to_domain(result)
            assert isinstance(source, LinkSource)
            return source

    async def _get_page_source(self, source_id: SourceId) -> PageSource | None:
        async with self.maker() as session:
            result = await session.get(PageSourceBase, source_id.value)
            if not result:
                return None
            source = SourceMapper.to_domain(result)
            assert isinstance(source, PageSource)
            return source

    async def _add_file_source(self) -> FileSource:
        source = make_file_source()
        async with self.maker() as session:
            session.add(SourceMapper.to_persistence(source))
            await session.commit()
        return source

    async def _add_link_source(self) -> LinkSource:
        source = make_link_source()
        async with self.maker() as session:
            session.add(SourceMapper.to_persistence(source))
            await session.commit()
        return source

    async def _add_page_source(self) -> PageSource:
        source = make_page_source()
        async with self.maker() as session:
            session.add(SourceMapper.to_persistence(source))
            await session.commit()
        return source

    async def test_get_file_source_success(self):
        # Arrange
        source = await self._add_file_source()

        # Act
        result = await self.source_repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_link_source_success(self):
        # Arrange
        source = await self._add_link_source()

        # Act
        result = await self.source_repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_page_source_success(self):
        # Arrange
        source = await self._add_page_source()

        # Act
        result = await self.source_repository.get_by_id(source.id)

        # Assert
        assert result == source

    async def test_get_source_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.source_repository.get_by_id(SourceId(uuid4()))

    async def test_add_file_source_success(self):
        # Arrange
        source = make_file_source()

        # Act
        await self.source_repository.add(source)

        # Assert
        saved_source = await self._get_file_source(source.id)
        assert saved_source == source

    async def test_add_link_source_success(self):
        # Arrange
        source = make_link_source()

        # Act
        await self.source_repository.add(source)

        # Assert
        saved_source = await self._get_link_source(source.id)
        assert saved_source == source

    async def test_add_page_source_success(self):
        # Arrange
        source = make_page_source()

        # Act
        await self.source_repository.add(source)

        # Assert
        saved_source = await self._get_page_source(source.id)
        assert saved_source == source

    async def test_save_file_source_success(self):
        # Arrange
        source = await self._add_file_source()
        source.title = Title("New File Source 123")

        # Act
        await self.source_repository.save(source)

        # Assert
        updated_source = await self._get_file_source(source.id)
        assert updated_source is not None
        assert updated_source.title == source.title

    async def test_save_link_source_success(self):
        # Arrange
        source = await self._add_link_source()
        source.url = Url("https://updated-example.com")

        # Act
        await self.source_repository.save(source)

        # Assert
        updated_source = await self._get_link_source(source.id)
        assert updated_source is not None
        assert updated_source.url == Url("https://updated-example.com")

    async def test_save_page_source_success(self):
        # Arrange
        source = await self._add_page_source()
        source.editable = False

        # Act
        await self.source_repository.save(source)

        # Assert
        updated_source = await self._get_page_source(source.id)
        assert updated_source is not None
        assert updated_source.editable is False

    async def test_remove_file_source_success(self):
        # Arrange
        source = await self._add_file_source()

        # Act
        await self.source_repository.remove(source)

        # Assert
        assert await self._exists(source.id) is False

    async def test_remove_link_source_success(self):
        # Arrange
        source = await self._add_link_source()

        # Act
        await self.source_repository.remove(source)

        # Assert
        assert await self._exists(source.id) is False

    async def test_remove_page_source_success(self):
        # Arrange
        source = await self._add_page_source()

        # Act
        await self.source_repository.remove(source)

        # Assert
        assert await self._exists(source.id) is False

    async def test_remove_nonexistent_source_success(self):
        # Arrange
        source = make_file_source()

        # Act & Assert
        await self.source_repository.remove(source)  # no error
