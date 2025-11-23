from abc import ABC
from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId
from common.domain.value_objects.title import Title

from luminary.source.domain.enums import FetchStatus, SourceType


@dataclass(frozen=True)
class SourceId(EntityId): ...


@dataclass
class Source(ABC):
    id: SourceId
    owner_id: UserId
    title: Title
    type: SourceType
    content_id: UUID | None
    fetched_at: DateTime | None
    fetch_status: FetchStatus
    created_at: DateTime

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def is_content_editable(self) -> bool:
        return False

    def update_title(self, title: str) -> None:
        self.title = Title(title)

    def title_matches(self, title: str) -> bool:
        return self.title.value == title

    def set_content(self, content_id: UUID) -> None:
        self.content_id = content_id

    def fetch(self, content_id: UUID, fetched_at: DateTime) -> None:
        self.content_id = content_id
        self.fetched_at = fetched_at
        self.fetch_status = FetchStatus.FETCHED

    def embed(self) -> None:
        self.fetch_status = FetchStatus.EMBEDDED

    def fail(self) -> None:
        self.fetch_status = FetchStatus.FAILED
