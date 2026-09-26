from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import FileId
from tests.unit.utils import MockClock, MockUUIDGenerator

from luminary.content.domain.entity.content import ContentId
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import SourceId
from luminary.source.domain.enums import SourceType
from luminary.source.domain.factories.source_factory import SourceFactory
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)


class TestSourceFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = SourceId(uuid4())
        self.owner_id = UserId(uuid4())
        self.content_id = ContentId(uuid4())
        self.created_at = DateTime(datetime.now(UTC))

        self.factory = SourceFactory(
            clock=MockClock(self.created_at),
            uuid_generator=MockUUIDGenerator(self.source_id.value),
        )

    def test_create_file_source(self) -> None:
        # Arrange
        file_id = FileId(uuid4())
        dto = FileSourceFactoryDTO(
            owner_id=self.owner_id, title="Test File", file_id=file_id
        )

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, FileSource)
        assert source.id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.type == SourceType.FILE
        assert source.created_at == self.created_at

    def test_create_link_source(self) -> None:
        # Arrange
        url = "https://example.com"
        dto = LinkSourceFactoryDTO(owner_id=self.owner_id, title="Test Link", url=url)

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, LinkSource)
        assert source.id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.type == SourceType.LINK
        assert source.url.value == url
        assert source.created_at == self.created_at

    def test_create_page_source(self) -> None:
        # Arrange
        dto = PageSourceFactoryDTO(
            owner_id=self.owner_id, title="Test Page", content_id=self.content_id
        )

        # Act
        source = self.factory.create(dto)

        # Assert
        assert isinstance(source, PageSource)
        assert source.id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == dto.title
        assert source.content_id == self.content_id
        assert source.type == SourceType.PAGE
        assert source.editable is True
        assert source.created_at == self.created_at

    def test_create_unsupported_type(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            self.factory.create("invalid")  # type: ignore
