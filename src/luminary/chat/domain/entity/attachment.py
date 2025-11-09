from dataclasses import dataclass
from uuid import UUID

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class Attachment:
    name: str
    content_id: UUID
    source_id: UUID | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Attachment name cannot be empty")
