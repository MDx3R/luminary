from abc import ABC
from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId
from common.domain.value_objects.title import Title

from luminary.source.domain.enums import SourceType


@dataclass(frozen=True)
class SourceId(EntityId): ...


@dataclass
class Source(ABC):
    id: SourceId
    owner_id: UserId
    title: Title
    type: SourceType
    content_id: UUID | None
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
