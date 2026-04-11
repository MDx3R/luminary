"""Integration tests for SourceReadRepository."""

from uuid import UUID, uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from tests.integration.sqlalchemy.utils import (
    add_file_source,
    add_link_source,
    add_page_source,
    persist_source,
)
from tests.unit.source.utils import make_file_source

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.infrastructure.database.postgres.sqlalchemy.repositories.source_read_repository import (
    SourceReadRepository,
)


@pytest.mark.asyncio
class TestSourceReadRepository:
    @pytest.fixture(autouse=True)
    def setup(self, maker, query_executor: QueryExecutor) -> None:
        self.maker = maker
        self.read_repo = SourceReadRepository(query_executor)

    async def _add_file_source(self, owner_id: UUID | None = None) -> FileSource:
        owner_id = owner_id or uuid4()
        return await add_file_source(maker=self.maker, owner_id=owner_id)

    async def _add_link_source(self, owner_id: UUID | None = None) -> LinkSource:
        owner_id = owner_id or uuid4()
        return await add_link_source(
            maker=self.maker, owner_id=owner_id, url="https://link.test"
        )

    async def _add_page_source(self, owner_id: UUID | None = None) -> PageSource:
        owner_id = owner_id or uuid4()
        return await add_page_source(
            maker=self.maker, owner_id=owner_id, editable=False
        )

    # --- get_by_id ---

    async def test_get_by_id_file_source_returns_read_model(self) -> None:
        # Arrange
        source = await self._add_file_source()
        owner_id = source.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(source.id.value, owner_id)

        # Assert
        assert result.id == source.id.value
        assert result.title == source.title.value
        assert result.type == "file"
        assert result.file_id == source.file_id.value
        assert result.url is None
        assert result.editable is None

    async def test_get_by_id_link_source_returns_read_model(self) -> None:
        # Arrange
        source = await self._add_link_source()
        owner_id = source.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(source.id.value, owner_id)

        # Assert
        assert result.id == source.id.value
        assert result.title == source.title.value
        assert result.type == "link"
        assert result.url == "https://link.test"
        assert result.file_id is None
        assert result.editable is None

    async def test_get_by_id_page_source_returns_read_model(self) -> None:
        # Arrange
        source = await self._add_page_source()
        owner_id = source.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(source.id.value, owner_id)

        # Assert
        assert result.id == source.id.value
        assert result.type == "page"
        assert result.editable is False
        assert result.url is None
        assert result.file_id is None

    async def test_get_by_id_not_found_raises(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(uuid4(), owner_id)

    async def test_get_by_id_wrong_owner_raises(self) -> None:
        # Arrange
        source = await self._add_file_source()
        other_owner = uuid4()
        assert other_owner != source.owner_id.value

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(source.id.value, other_owner)

    async def test_get_by_id_soft_deleted_raises(self) -> None:
        # Arrange
        owner_id = uuid4()
        source = make_file_source(owner_id=owner_id)
        source.is_deleted = True
        await persist_source(self.maker, source)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(source.id.value, source.owner_id.value)

    # --- list_by_owner ---

    async def test_list_by_owner_empty(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert list(result) == []

    async def test_list_by_owner_returns_all_ordered_by_created_at_desc(
        self,
    ) -> None:
        # Arrange
        owner_id = uuid4()
        s1 = await add_file_source(maker=self.maker, owner_id=owner_id, title="First")
        s2 = await add_link_source(maker=self.maker, owner_id=owner_id, title="Second")
        s3 = await add_page_source(maker=self.maker, owner_id=owner_id, title="Third")

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert {r.id for r in result} == {s1.id.value, s2.id.value, s3.id.value}
        assert {r.title for r in result} == {"First", "Second", "Third"}
        assert result[0].created_at >= result[1].created_at >= result[2].created_at

    async def test_list_by_owner_excludes_other_owner(self) -> None:
        # Arrange
        owner_a = uuid4()
        owner_b = uuid4()
        await self._add_file_source(owner_id=owner_a)

        # Act
        result = await self.read_repo.list_by_owner(owner_b)

        # Assert
        assert list(result) == []

    async def test_list_by_owner_excludes_soft_deleted(self) -> None:
        # Arrange
        owner_id = uuid4()
        source = make_file_source(owner_id=owner_id)
        source.is_deleted = True
        await persist_source(self.maker, source)

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert list(result) == []
