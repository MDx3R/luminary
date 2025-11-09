from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source
from luminary.source.domain.enums import FetchStatus, SourceType
from luminary.source.domain.value_objects.file_meta import FileMeta


class _TestSource(Source):
    pass


class TestSourceEntity:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = uuid4()
        self.owner_id = uuid4()
        self.created_at = DateTime(datetime.now(UTC))
        self.title = Title("Test Source")

        # NOTE: Define and create concrete _TestSource
        # as Source is abstract
        self.source = _TestSource(
            source_id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            type=SourceType.FILE,
            content_id=None,
            created_at=self.created_at,
        )

    def test_update_title(self) -> None:
        # Arrange
        new_title = "New Title"

        # Act
        self.source.update_title(new_title)

        # Assert
        assert self.source.title.value == new_title

    def test_set_content(self) -> None:
        # Arrange
        content_id = uuid4()

        # Act
        self.source.set_content(content_id)

        # Assert
        assert self.source.content_id == content_id


class TestFileSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = uuid4()
        self.owner_id = uuid4()
        self.content_id = uuid4()
        self.title = "Test File"
        self.meta = FileMeta(
            filename="test.txt", mime_type="text/plain", filesize=100, checksum="abc123"
        )
        self.created_at = DateTime(datetime.now(UTC))

        self.source = FileSource(
            source_id=self.source_id,
            owner_id=self.owner_id,
            title=Title(self.title),
            meta=self.meta,
            content_id=self.content_id,
            type=SourceType.FILE,
            created_at=self.created_at,
        )

    def test_create_file_source_success(self) -> None:
        # Act
        source = FileSource.create(
            source_id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            meta=self.meta,
            created_at=self.created_at,
        )

        # Assert
        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == self.title
        assert source.type == SourceType.FILE
        assert source.meta == self.meta
        assert source.created_at == self.created_at

    def test_create_file_source_invalid_meta(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            FileMeta(
                filename="",  # invalid empty filename
                mime_type="text/plain",
                filesize=100,
                checksum="abc123",
            )


class TestLinkSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = uuid4()
        self.owner_id = uuid4()
        self.title = "Test Link"
        self.url = "https://example.com"
        self.created_at = DateTime(datetime.now(UTC))

        self.link_source = LinkSource.create(
            source_id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            url=self.url,
            created_at=self.created_at,
        )

    def test_create_link_source_success(self) -> None:
        source = self.link_source

        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == self.title
        assert source.type == SourceType.LINK
        assert source.url.value == self.url
        assert source.fetched_at is None
        assert source.fetch_status == FetchStatus.NOT_FETCHED
        assert source.created_at == self.created_at

    def test_create_link_source_invalid_url(self) -> None:
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            LinkSource.create(
                source_id=uuid4(),
                owner_id=uuid4(),
                title="Test",
                url="",
                created_at=DateTime(datetime.now(UTC)),
            )

    def test_fetch_success(self) -> None:
        source = replace(self.link_source)
        fetched_at = DateTime(datetime.now(UTC))

        # Act
        source.fetch(fetched_at)

        # Assert
        assert source.fetched_at == fetched_at
        assert source.fetch_status == FetchStatus.FETCHED

    def test_fetch_fail(self) -> None:
        source = replace(self.link_source)

        # Act
        source.fail()

        # Assert
        assert source.fetch_status == FetchStatus.FAILED


class TestPageSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = uuid4()
        self.owner_id = uuid4()
        self.title = "Test Page"
        self.created_at = DateTime(datetime.now(UTC))

        self.base_page = PageSource.create(
            source_id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            created_at=self.created_at,
        )

    def test_create_page_source_success(self) -> None:
        source = self.base_page

        assert source.source_id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == self.title
        assert source.type == SourceType.PAGE
        assert source.editable is True
        assert source.created_at == self.created_at

    def test_lock_page(self) -> None:
        source = replace(self.base_page)
        assert source.editable is True

        # Act
        source.lock()

        # Assert
        assert source.editable is False

    def test_unlock_page(self) -> None:
        source = replace(self.base_page)
        source.editable = False
        assert source.editable is False

        # Act
        source.unlock()

        # Assert
        assert source.editable is True

    def test_lock_page_idempotent(self) -> None:
        source = replace(self.base_page)
        assert source.editable is True

        # Act
        source.lock()

        # Assert
        assert source.editable is False

        # Act
        source.lock()

        # Assert
        assert source.editable is False

    def test_unlock_page_idempotent(self) -> None:
        source = replace(self.base_page)
        source.editable = False
        assert source.editable is False

        # Act
        source.unlock()

        # Assert
        assert source.editable is True

        # Act
        source.unlock()

        # Assert
        assert source.editable is True
