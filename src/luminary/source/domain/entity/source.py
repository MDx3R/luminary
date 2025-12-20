from dataclasses import dataclass

from common.domain.interfaces.entity import IEntity
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId
from common.domain.value_objects.title import Title

from luminary.content.domain.entity.content import ContentId
from luminary.source.domain.enums import FetchStatus, SourceType
from luminary.source.domain.events.events import (
    SourceEmbeddedEvent,
    SourceFailedEvent,
    SourceFetchedEvent,
    SourceTitleChangedEvent,
)


@dataclass(frozen=True)
class SourceId(EntityId): ...


@dataclass
class Source(IEntity):
    id: SourceId
    owner_id: UserId
    title: Title
    type: SourceType
    content_id: ContentId | None
    fetched_at: DateTime | None
    fetch_status: FetchStatus
    created_at: DateTime

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def is_content_editable(self) -> bool:
        return False

    def update_title(self, title: str) -> None:
        if self.title_matches(title):
            return

        self.title = Title(title)
        self._record_event(
            SourceTitleChangedEvent(source_id=self.id.value, title=title)
        )

    def title_matches(self, title: str) -> bool:
        return self.title.value == title

    def can_be_fetched(self) -> bool:
        return self.fetch_status == FetchStatus.NOT_FETCHED

    def can_be_embedded(self) -> bool:
        return self.fetch_status == FetchStatus.FETCHED

    def fetch(self, content_id: ContentId, fetched_at: DateTime) -> None:
        self.content_id = content_id
        self.fetched_at = fetched_at
        self.fetch_status = FetchStatus.FETCHED
        self._record_event(
            SourceFetchedEvent(
                source_id=self.id.value,
                content_id=content_id.value,
                fetched_at=fetched_at.value,
            )
        )

    def embed(self) -> None:
        self.fetch_status = FetchStatus.EMBEDDED
        self._record_event(SourceEmbeddedEvent(source_id=self.id.value))

    def fail(self) -> None:
        self.fetch_status = FetchStatus.FAILED
        self._record_event(SourceFailedEvent(source_id=self.id.value))
