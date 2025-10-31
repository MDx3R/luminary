from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass
class Source:
    source_id: UUID
    user_id: UUID
    name: str
    created_at: DateTime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Source name cannot be empty")

    @classmethod
    def create(
        cls,
        source_id: UUID,
        user_id: UUID,
        name: str,
        created_at: DateTime,
    ) -> Self:
        return cls(
            source_id=source_id, user_id=user_id, name=name, created_at=created_at
        )
    
    def update_name(self, name: str) -> None:
        self.name = name
