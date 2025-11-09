from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from tests.unit.utils import MockClock, MockUUIDGenerator

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.enums import SourceType
from luminary.source.domain.factories.source_factory import SourceFactory
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)
from luminary.source.domain.value_objects.file_meta import FileMeta


class TestSourceFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = uuid4()
        self.owner_id = uuid4()
        self.created_at = DateTime(datetime.now(UTC))

        self.factory = SourceFactory(
            clock=MockClock(self.created_at),
            uuid_generator=MockUUIDGenerator(self.source_id),
        )

    def test_create_file_source(self) -> None:
        # Arrange
        file_id = uuid4()
        meta = FileMeta(
            filename="test.txt",
            mime_type="text/plain",
            filesize=100,
            checksum="abc123",
        )
        dto = FileSourceFactoryDTO(
            owner_id=self.owner_id, title="Test File", meta=meta, file_id=file_id
        )

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, FileSource)
        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.type == SourceType.FILE
        assert source.meta == meta
        assert source.created_at == self.created_at

    def test_create_link_source(self) -> None:
        # Arrange
        url = "https://example.com"
        dto = LinkSourceFactoryDTO(owner_id=self.owner_id, title="Test Link", url=url)

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, LinkSource)
        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.type == SourceType.LINK
        assert source.url.value == url
        assert source.created_at == self.created_at

    def test_create_page_source(self) -> None:
        # Arrange
        dto = PageSourceFactoryDTO(owner_id=self.owner_id, title="Test Page")

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, PageSource)
        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.type == SourceType.PAGE
        assert source.editable is True
        assert source.created_at == self.created_at

    def test_create_unsupported_type(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            self.factory.create("invalid")  # type: ignore
