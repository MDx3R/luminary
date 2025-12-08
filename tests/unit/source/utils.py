from datetime import UTC, datetime
from uuid import UUID, uuid4

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


def make_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test Source",
    type: SourceType = SourceType.FILE,
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
    fetched_at: DateTime | None = None,
    fetch_status: FetchStatus = FetchStatus.NOT_FETCHED,
) -> Source:
    source_id = source_id or uuid4()
    owner_id = owner_id or uuid4()
    return Source(
        id=SourceId(source_id),
        owner_id=UserId(owner_id),
        title=Title(title),
        type=type,
        content_id=ContentId(content_id) if content_id else None,
        created_at=created_at or DateTime(datetime.now(UTC)),
        fetched_at=fetched_at,
        fetch_status=fetch_status,
    )


def make_file_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test File",
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
    file_id: UUID | None = None,
    fetched_at: DateTime | None = None,
    fetch_status: FetchStatus = FetchStatus.NOT_FETCHED,
) -> FileSource:
    source_id = source_id or uuid4()
    owner_id = owner_id or uuid4()
    return FileSource(
        id=SourceId(source_id),
        owner_id=UserId(owner_id),
        title=Title(title),
        type=SourceType.FILE,
        content_id=ContentId(content_id) if content_id else None,
        created_at=created_at or DateTime(datetime.now(UTC)),
        file_id=FileId(file_id or uuid4()),
        fetched_at=fetched_at,
        fetch_status=fetch_status,
    )


def make_link_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test Link",
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
    url: str = "https://example.com",
    fetched_at: DateTime | None = None,
    fetch_status: FetchStatus = FetchStatus.NOT_FETCHED,
) -> LinkSource:
    source_id = source_id or uuid4()
    owner_id = owner_id or uuid4()
    return LinkSource(
        id=SourceId(source_id),
        owner_id=UserId(owner_id),
        title=Title(title),
        type=SourceType.LINK,
        content_id=ContentId(content_id) if content_id else None,
        created_at=created_at or DateTime(datetime.now(UTC)),
        url=Url(url),
        fetched_at=fetched_at,
        fetch_status=fetch_status,
    )


def make_page_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test Page",
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
    editable: bool = True,
    fetched_at: DateTime | None = None,
) -> PageSource:
    source_id = source_id or uuid4()
    owner_id = owner_id or uuid4()
    # NOTE: Content ID cannot be None for PageSource
    content_id = content_id or uuid4()

    return PageSource(
        id=SourceId(source_id),
        owner_id=UserId(owner_id),
        title=Title(title),
        type=SourceType.PAGE,
        content_id=ContentId(content_id) if content_id else None,
        created_at=created_at or DateTime(datetime.now(UTC)),
        editable=editable,
        fetched_at=fetched_at,
        fetch_status=FetchStatus.FETCHED,
    )
