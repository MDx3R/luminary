from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from common.domain.events.domain_event import DomainEvent

from luminary.source.domain.enums import FetchStatus


@dataclass(frozen=True)
class SourceEvent(DomainEvent):
    source_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.source_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "source"


@dataclass(frozen=True)
class SourceCreatedEvent(SourceEvent):
    fetch_status: FetchStatus


@dataclass(frozen=True)
class SourceTitleChangedEvent(SourceEvent):
    title: str


@dataclass(frozen=True)
class SourceFetchedEvent(SourceEvent):
    content_id: UUID
    fetched_at: datetime


@dataclass(frozen=True)
class SourceEmbeddedEvent(SourceEvent):
    pass


@dataclass(frozen=True)
class SourceFailedEvent(SourceEvent):
    pass


@dataclass(frozen=True)
class SourceDeletedEvent(SourceEvent):
    pass


@dataclass(frozen=True)
class PageSourceLockedEvent(SourceEvent):
    pass


@dataclass(frozen=True)
class PageSourceUnlockedEvent(SourceEvent):
    pass
