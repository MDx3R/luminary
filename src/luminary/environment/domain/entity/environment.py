from dataclasses import dataclass, field
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass
class Environment:
    environment_id: UUID
    name: str
    description: str | None
    user_id: UUID
    model_id: UUID
    assistant_id: UUID
    edited_at: DateTime
    created_at: DateTime
    files: list[UUID] = field(default_factory=list[UUID])

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Environment name cannot be empty")

    def add_file(self, file_id: UUID) -> None:
        if self.has_file(file_id):
            return

        self.files.append(file_id)

    def remove_file(self, file_id: UUID) -> None:
        self.files = [f for f in self.files if f != file_id]

    def has_file(self, file_id: UUID) -> bool:
        return file_id in self.files

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        environment_id: UUID,
        name: str,
        description: str | None,
        user_id: UUID,
        model_id: UUID,
        assistant_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(
            environment_id=environment_id,
            name=name,
            description=description,
            user_id=user_id,
            model_id=model_id,
            assistant_id=assistant_id,
            edited_at=created_at,
            created_at=created_at,
        )
