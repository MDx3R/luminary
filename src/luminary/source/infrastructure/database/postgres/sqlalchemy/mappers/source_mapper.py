from functools import singledispatchmethod

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url
from common.infrastructure.database.sqlalchemy.models.base import Base
from luminary_files.domain.entity.file import FileId

from luminary.content.domain.entity.content import ContentId
from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import SourceType
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
        fetched_at = None
        if base.fetched_at:
            fetched_at = DateTime(base.fetched_at)
        content_id = None
        if base.content_id:
            content_id = ContentId(base.content_id)

        return FileSource(
            id=SourceId(base.source_id),
            owner_id=UserId(base.owner_id),
            title=Title(base.title),
            type=SourceType.FILE,
            content_id=content_id,
            file_id=FileId(base.file_id),
            fetched_at=fetched_at,
            fetch_status=base.fetch_status,
            created_at=DateTime(base.created_at),
            is_deleted=base.is_deleted,
        )

    @to_domain.register
    @classmethod
    def _(cls, base: LinkSourceBase) -> LinkSource:
        fetched_at = None
        if base.fetched_at:
            fetched_at = DateTime(base.fetched_at)
        content_id = None
        if base.content_id:
            content_id = ContentId(base.content_id)

        return LinkSource(
            id=SourceId(base.source_id),
            owner_id=UserId(base.owner_id),
            title=Title(base.title),
            type=SourceType.LINK,
            content_id=content_id,
            url=Url(base.url),
            fetched_at=fetched_at,
            fetch_status=base.fetch_status,
            created_at=DateTime(base.created_at),
            is_deleted=base.is_deleted,
        )

    @to_domain.register
    @classmethod
    def _(cls, base: PageSourceBase) -> PageSource:
        fetched_at = None
        if base.fetched_at:
            fetched_at = DateTime(base.fetched_at)
        content_id = None
        if base.content_id:
            content_id = ContentId(base.content_id)

        return PageSource(
            id=SourceId(base.source_id),
            owner_id=UserId(base.owner_id),
            title=Title(base.title),
            type=SourceType.PAGE,
            content_id=content_id,
            editable=base.editable,
            fetched_at=fetched_at,
            fetch_status=base.fetch_status,
            created_at=DateTime(base.created_at),
            is_deleted=base.is_deleted,
        )

    @singledispatchmethod
    @classmethod
    def to_persistence(cls, source: Source) -> SourceBase:
        raise TypeError(f"Unsupported source type: {type(source).__name__}")

    @to_persistence.register
    @classmethod
    def _(cls, source: FileSource) -> FileSourceBase:
        fetched_at = None
        if source.fetched_at:
            fetched_at = source.fetched_at.value
        content_id = None
        if source.content_id:
            content_id = source.content_id.value

        return FileSourceBase(
            source_id=source.id.value,
            owner_id=source.owner_id.value,
            title=source.title.value,
            type=source.type.value,
            content_id=content_id,
            file_id=source.file_id.value,
            fetched_at=fetched_at,
            fetch_status=source.fetch_status,
            created_at=source.created_at.value,
            is_deleted=source.is_deleted,
        )

    @to_persistence.register
    @classmethod
    def _(cls, source: LinkSource) -> LinkSourceBase:
        fetched_at = None
        if source.fetched_at:
            fetched_at = source.fetched_at.value
        content_id = None
        if source.content_id:
            content_id = source.content_id.value

        return LinkSourceBase(
            source_id=source.id.value,
            owner_id=source.owner_id.value,
            title=source.title.value,
            type=source.type.value,
            content_id=content_id,
            url=source.url.value,
            fetched_at=fetched_at,
            fetch_status=source.fetch_status,
            created_at=source.created_at.value,
            is_deleted=source.is_deleted,
        )

    @to_persistence.register
    @classmethod
    def _(cls, source: PageSource) -> PageSourceBase:
        fetched_at = None
        if source.fetched_at:
            fetched_at = source.fetched_at.value
        content_id = None
        if source.content_id:
            content_id = source.content_id.value

        return PageSourceBase(
            source_id=source.id.value,
            owner_id=source.owner_id.value,
            title=source.title.value,
            type=source.type.value,
            content_id=content_id,
            editable=source.editable,
            fetched_at=fetched_at,
            fetch_status=source.fetch_status,
            created_at=source.created_at.value,
            is_deleted=source.is_deleted,
        )


class SourceReadMapper:
    @singledispatchmethod
    @classmethod
    def to_read(cls, base: SourceBase) -> SourceReadModel:
        return SourceReadModel(
            id=base.source_id,
            title=base.title,
            type=base.type.value,
            fetch_status=base.fetch_status.value,
            created_at=base.created_at,
        )

    @to_read.register
    @classmethod
    def _(cls, base: FileSourceBase) -> SourceReadModel:
        return SourceReadModel(
            id=base.source_id,
            title=base.title,
            type=base.type.value,
            fetch_status=base.fetch_status.value,
            created_at=base.created_at,
            file_id=base.file_id,
        )

    @to_read.register
    @classmethod
    def _(cls, base: LinkSourceBase) -> SourceReadModel:
        return SourceReadModel(
            id=base.source_id,
            title=base.title,
            type=base.type.value,
            fetch_status=base.fetch_status.value,
            created_at=base.created_at,
            url=base.url,
        )

    @to_read.register
    @classmethod
    def _(cls, base: PageSourceBase) -> SourceReadModel:
        return SourceReadModel(
            id=base.source_id,
            title=base.title,
            type=base.type.value,
            fetch_status=base.fetch_status.value,
            created_at=base.created_at,
            editable=base.editable,
        )
