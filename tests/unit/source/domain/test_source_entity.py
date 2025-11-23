from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url
from luminary_files.domain.entity.file import FileId

from luminary.content.domain.entity.content import ContentId
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import FetchStatus, SourceType


class _TestSource(Source):
    pass


class TestSourceEntity:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = SourceId(uuid4())
        self.owner_id = UserId(uuid4())
        self.created_at = DateTime(datetime.now(UTC))
        self.title = Title("Test Source")

        # NOTE: Define and create concrete _TestSource
        # as Source is abstract
        self.source = _TestSource(
            id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            type=SourceType.FILE,
            content_id=None,
            created_at=self.created_at,
            fetched_at=None,
            fetch_status=FetchStatus.NOT_FETCHED,
        )

    def test_update_title(self) -> None:
        # Arrange
        new_title = "New Title"

        # Act
        self.source.update_title(new_title)

        # Assert
        assert self.source.title.value == new_title

    def test_title_matches(self) -> None:
        # Act & Assert
        assert self.source.title_matches(self.source.title.value)
        assert not self.source.title_matches("random title")

    def test_is_owned_by(self) -> None:
        # Act & Assert
        assert self.source.is_owned_by(self.source.owner_id)
        assert not self.source.is_owned_by(UserId(uuid4()))

    def test_is_content_editable(self) -> None:
        # Act & Assert
        assert not self.source.is_content_editable()


class TestFileSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = SourceId(uuid4())
        self.owner_id = UserId(uuid4())
        self.content_id = ContentId(uuid4())
        self.file_id = FileId(uuid4())
        self.title = "Test File"
        self.created_at = DateTime(datetime.now(UTC))

        self.source = FileSource(
            id=self.source_id,
            owner_id=self.owner_id,
            title=Title(self.title),
            content_id=self.content_id,
            type=SourceType.FILE,
            file_id=self.file_id,
            created_at=self.created_at,
            fetched_at=None,
            fetch_status=FetchStatus.NOT_FETCHED,
        )

    def test_create_file_source_success(self) -> None:
        # Act
        source = FileSource.create(
            id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            file_id=self.file_id,
            created_at=self.created_at,
        )

        # Assert
        assert source.id == self.source_id
        assert source.owner_id == self.owner_id
        assert source.title.value == self.title
        assert source.type == SourceType.FILE
        assert source.file_id == self.file_id
        assert source.created_at == self.created_at

    def test_is_content_editable(self) -> None:
        # Act & Assert
        assert not self.source.is_content_editable()


class TestLinkSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = SourceId(uuid4())
        self.owner_id = UserId(uuid4())
        self.title = "Test Link"
        self.url = "https://example.com"
        self.created_at = DateTime(datetime.now(UTC))

        self.link_source = LinkSource(
            id=self.source_id,
            owner_id=self.owner_id,
            title=Title(self.title),
            url=Url(self.url),
            content_id=None,
            type=SourceType.LINK,
            fetched_at=None,
            fetch_status=FetchStatus.NOT_FETCHED,
            created_at=self.created_at,
        )

    def test_create_link_source_success(self) -> None:
        source = LinkSource.create(
            id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            url=self.url,
            created_at=self.created_at,
        )

        assert source.id == self.source_id
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
                id=self.source_id,
                owner_id=self.owner_id,
                title="Test",
                url="",
                created_at=DateTime(datetime.now(UTC)),
            )

    def test_fetch_success(self) -> None:
        content_id = ContentId(uuid4())
        source = replace(self.link_source)
        fetched_at = DateTime(datetime.now(UTC))

        # Act
        source.fetch(content_id, fetched_at)

        # Assert
        assert source.fetched_at == fetched_at
        assert source.fetch_status == FetchStatus.FETCHED

    def test_fetch_fail(self) -> None:
        source = replace(self.link_source)

        # Act
        source.fail()

        # Assert
        assert source.fetch_status == FetchStatus.FAILED

    def test_is_content_editable(self) -> None:
        # Act & Assert
        assert not self.link_source.is_content_editable()


class TestPageSource:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.source_id = SourceId(uuid4())
        self.owner_id = UserId(uuid4())
        self.content_id = ContentId(uuid4())
        self.title = "Test Page"
        self.created_at = DateTime(datetime.now(UTC))

        self.base_page = PageSource(
            id=self.source_id,
            owner_id=self.owner_id,
            title=Title(self.title),
            content_id=self.content_id,
            type=SourceType.PAGE,
            editable=True,
            created_at=self.created_at,
            fetched_at=None,
            fetch_status=FetchStatus.FETCHED,
        )

    def test_create_page_source_success(self) -> None:
        source = PageSource.create(
            id=self.source_id,
            owner_id=self.owner_id,
            title=self.title,
            content_id=self.content_id,
            created_at=self.created_at,
        )

        assert source.id == self.source_id
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

    def test_is_content_editable(self) -> None:
        # Arrange
        source = replace(self.base_page)
        source.editable = True

        # Act & Assert
        assert source.is_content_editable()

        # Arrange
        source = replace(self.base_page)
        source.editable = False

        # Act & Assert
        assert not source.is_content_editable()
