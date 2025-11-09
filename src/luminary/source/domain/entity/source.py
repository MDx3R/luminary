from abc import ABC
from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title

from luminary.source.domain.enums import SourceType


@dataclass
class Source(ABC):
    source_id: UUID
    owner_id: UUID
    title: Title
    type: SourceType
    content_id: UUID | None
    created_at: DateTime

    def update_title(self, title: str) -> None:
        self.title = Title(title)

    def set_content(self, content_id: UUID) -> None:
        self.content_id = content_id
