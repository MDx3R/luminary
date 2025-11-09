from functools import singledispatchmethod

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url
from common.infrastructure.database.sqlalchemy.models.base import Base

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source
from luminary.source.domain.enums import SourceType
from luminary.source.domain.value_objects.file_meta import FileMeta
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    FileSourceBase,
    LinkSourceBase,
    PageSourceBase,
    SourceBase,
)


class SourceMapper:
    @singledispatchmethod
    @classmethod
    def to_domain(cls, base: Base) -> Source:
        raise TypeError(f"Unsupported base type: {type(base).__name__}")

    @to_domain.register
    @classmethod
    def _(cls, base: FileSourceBase) -> FileSource:
        return FileSource(
            source_id=base.source_id,
            owner_id=base.owner_id,
            title=Title(base.title),
            type=SourceType.FILE,
            content_id=base.content_id,
            meta=FileMeta(
                filename=base.filename,
                mime_type=base.mime_type,
                filesize=base.filesize,
                checksum=base.checksum,
            ),
            created_at=DateTime(base.created_at),
        )

    @to_domain.register
    @classmethod
    def _(cls, base: LinkSourceBase) -> LinkSource:
        fetched_at = None
        if base.fetched_at:
            fetched_at = DateTime(base.fetched_at)

        return LinkSource(
            source_id=base.source_id,
            owner_id=base.owner_id,
            title=Title(base.title),
            type=SourceType.LINK,
            content_id=base.content_id,
            url=Url(base.url),
            fetched_at=fetched_at,
            fetch_status=base.fetch_status,
            created_at=DateTime(base.created_at),
        )

    @to_domain.register
    @classmethod
    def _(cls, base: PageSourceBase) -> PageSource:
        return PageSource(
            source_id=base.source_id,
            owner_id=base.owner_id,
            title=Title(base.title),
            type=SourceType.PAGE,
            content_id=base.content_id,
            editable=base.editable,
            created_at=DateTime(base.created_at),
        )

    @singledispatchmethod
    @classmethod
    def to_persistence(cls, source: Source) -> SourceBase:
        raise TypeError(f"Unsupported source type: {type(source).__name__}")

    @to_persistence.register
    @classmethod
    def _(cls, source: FileSource) -> FileSourceBase:
        return FileSourceBase(
            source_id=source.source_id,
            owner_id=source.owner_id,
            title=source.title.value,
            type=source.type.value,
            content_id=source.content_id,
            created_at=source.created_at.value,
            filename=source.meta.filename,
            mime_type=source.meta.mime_type,
            filesize=source.meta.filesize,
            checksum=source.meta.checksum,
        )

    @to_persistence.register
    @classmethod
    def _(cls, source: LinkSource) -> LinkSourceBase:
        return LinkSourceBase(
            source_id=source.source_id,
            owner_id=source.owner_id,
            title=source.title.value,
            type=source.type.value,
            content_id=source.content_id,
            created_at=source.created_at.value,
            url=source.url.value,
            fetched_at=source.fetched_at.value if source.fetched_at else None,
            fetch_status=source.fetch_status,
        )

    @to_persistence.register
    @classmethod
    def _(cls, source: PageSource) -> PageSourceBase:
        return PageSourceBase(
            source_id=source.source_id,
            owner_id=source.owner_id,
            title=source.title.value,
            type=source.type.value,
            content_id=source.content_id,
            created_at=source.created_at.value,
            editable=source.editable,
        )
