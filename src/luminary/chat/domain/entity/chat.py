from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass
class Chat:
    chat_id: UUID
    folder_id: UUID | None
    name: str
    created_at: DateTime

    def __post_init__(self) -> None:
        self._validate_name(self.name)

    def _validate_name(self, name: str) -> None:
        if not name.strip():
            raise InvariantViolationError("Chat name cannot be empty")

    def change_name(self, new_name: str) -> None:
        self._validate_name(new_name)
        self.name = new_name

    @classmethod
    def create(
        cls,
        chat_id: UUID,
        folder_id: UUID | None,
        name: str,
        created_at: DateTime,
    ) -> Self:
        return cls(
            chat_id=chat_id, folder_id=folder_id, name=name, created_at=created_at
        )
