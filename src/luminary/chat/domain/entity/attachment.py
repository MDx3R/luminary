from dataclasses import dataclass
from uuid import UUID

from common.domain.exceptions import InvariantViolationError

from luminary.source.domain.entity.source import SourceId


@dataclass(frozen=True)
class Attachment:
    name: str
    content_id: UUID
    source_id: SourceId | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Attachment name cannot be empty")
