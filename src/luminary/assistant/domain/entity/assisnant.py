from dataclasses import dataclass
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import EntityId, UserId


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


@dataclass(frozen=True)
class AssistantId(EntityId): ...


@dataclass
class Assistant:
    id: AssistantId
    owner_id: UserId
    info: AssistantInfo
    instructions: Instructions
    is_deleted: bool

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def change_name(self, new_name: str) -> None:
        self.info = AssistantInfo(new_name, self.info.description)

    def change_description(self, new_description: str) -> None:
        self.info = AssistantInfo(self.info.name, new_description)

    def change_instructions(self, new_instructions: Instructions) -> None:
        self.instructions = new_instructions

    def delete(self) -> None:
        self.is_deleted = True

    @classmethod
    def create(
        cls,
        id: AssistantId,
        owner_id: UserId,
        name: str,
        description: str,
        instructions: Instructions,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            info=AssistantInfo(name, description),
            instructions=instructions,
            is_deleted=False,
        )
