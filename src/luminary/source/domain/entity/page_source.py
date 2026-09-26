from dataclasses import dataclass
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title

from luminary.content.domain.entity.content import ContentId
from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import FetchStatus, SourceType
from luminary.source.domain.events.events import (
    PageSourceLockedEvent,
    PageSourceUnlockedEvent,
    SourceCreatedEvent,
    SourceFetchedEvent,
)


@dataclass
class PageSource(Source):
    editable: bool

    def __post_init__(self) -> None:
        if self.content_id is None:
            raise InvariantViolationError("Page source must always refer to content")
        if self.fetch_status not in {
            FetchStatus.FETCHED,
            FetchStatus.EMBEDDED,
            FetchStatus.FAILED,
        }:
            raise InvariantViolationError(
                "Page source must have fetched/embedded/failed status"
            )

    def is_content_editable(self) -> bool:
        return self.editable

    def lock(self) -> None:
        self.editable = False
        self._record_event(PageSourceLockedEvent(source_id=self.id.value))

    def unlock(self) -> None:
        self.editable = True
        self._record_event(PageSourceUnlockedEvent(source_id=self.id.value))

    @classmethod
    def create(
        cls,
        id: SourceId,
        owner_id: UserId,
        title: str,
        content_id: ContentId,
        created_at: DateTime,
    ) -> Self:
        page = cls(
            id=id,
            owner_id=owner_id,
            title=Title(title),
            type=SourceType.PAGE,
            content_id=content_id,
            fetch_status=FetchStatus.FETCHED,
            editable=True,
            fetched_at=created_at,
            created_at=created_at,
            is_deleted=False,
        )
        page._record_event(
            SourceCreatedEvent(source_id=id.value, fetch_status=page.fetch_status)
        )
        page._record_event(
            SourceFetchedEvent(
                source_id=id.value,
                content_id=content_id.value,
                fetched_at=created_at.value,
            )
        )

        return page
