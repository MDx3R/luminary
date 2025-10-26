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


@dataclass(frozen=True)
class AssistantInfo:
    name: str
    description: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Assistant name cannot be empty")
        if not self.description.strip():
            raise InvariantViolationError("Assistant description cannot be empty")


@dataclass
class Assistant:
    assistant_id: UUID
    user_id: UUID
    info: AssistantInfo
    instructions: Instructions

    def change_name(self, new_name: str) -> None:
        self.info = AssistantInfo(new_name, self.info.description)

    def change_description(self, new_description: str) -> None:
        self.info = AssistantInfo(self.info.name, new_description)

    def change_instructions(self, new_instructions: Instructions) -> None:
        self.instructions = new_instructions

    @classmethod
    def create(
        cls,
        assistant_id: UUID,
        user_id: UUID,
        name: str,
        description: str,
        instructions: Instructions,
    ) -> Self:
        return cls(
            assistant_id=assistant_id,
            user_id=user_id,
            info=AssistantInfo(name, description),
            instructions=instructions,
        )
