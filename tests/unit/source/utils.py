from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source
from luminary.source.domain.enums import FetchStatus, SourceType
from luminary.source.domain.value_objects.file_meta import FileMeta


def make_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test Source",
    type: SourceType = SourceType.FILE,
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
) -> Source:
    return Source(
        source_id=source_id or uuid4(),
        owner_id=owner_id or uuid4(),
        title=Title(title),
        type=type,
        content_id=content_id,
        created_at=created_at or DateTime(datetime.now(UTC)),
    )


def make_file_source(  # noqa: PLR0913
    *,
    source_id: UUID | None = None,
    owner_id: UUID | None = None,
    title: str = "Test File",
    content_id: UUID | None = None,
    created_at: DateTime | None = None,
    meta: FileMeta | None = None,
) -> FileSource:
    if meta is None:
        meta = FileMeta(
            filename="test.txt",
            mime_type="text/plain",
            filesize=100,
            checksum="abc123",
        )

    return FileSource(
        source_id=source_id or uuid4(),
        owner_id=owner_id or uuid4(),
        title=Title(title),
        type=SourceType.FILE,
        content_id=content_id,
        created_at=created_at or DateTime(datetime.now(UTC)),
        meta=meta,
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
    return LinkSource(
        source_id=source_id or uuid4(),
        owner_id=owner_id or uuid4(),
        title=Title(title),
        type=SourceType.LINK,
        content_id=content_id,
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
) -> PageSource:
    return PageSource(
        source_id=source_id or uuid4(),
        owner_id=owner_id or uuid4(),
        title=Title(title),
        type=SourceType.PAGE,
        content_id=content_id,
        created_at=created_at or DateTime(datetime.now(UTC)),
        editable=editable,
    )
