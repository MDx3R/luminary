from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class Instructions:
    prompt: str

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise InvariantViolationError("Instructions prompt cannot be empty")


@dataclass
class Assistant:
    assistant_id: UUID
    user_id: UUID
    name: str
    description: str
    instructions: Instructions | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Assistant name cannot be empty")
        if not self.description.strip():
            raise InvariantViolationError("Assistant description cannot be empty")

    def change_name(self, new_name: str) -> None:
        if not new_name.strip():
            raise InvariantViolationError("New assistant name cannot be empty")
        self.name = new_name

    def change_description(self, new_description: str) -> None:
        if not new_description.strip():
            raise InvariantViolationError("New assistant description cannot be empty")
        self.description = new_description

    def change_instructions(self, new_instructions: Instructions) -> None:
        self.instructions = new_instructions

    def remove_instructions(self) -> None:
        self.instructions = None

    @classmethod
    def create(
        cls,
        assistant_id: UUID,
        user_id: UUID,
        name: str,
        description: str,
        instructions: Instructions | None,
    ) -> Self:
        return cls(assistant_id, user_id, name, description, instructions)
