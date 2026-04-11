from dataclasses import dataclass
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.interfaces.entity import Entity
from common.domain.value_objects.id import EntityId, UserId

from luminary.assistant.domain.enums import AssistantType
from luminary.assistant.domain.events.events import (
    AssistantCreatedEvent,
    AssistantDeletedEvent,
    AssistantInfoChangedEvent,
)


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
class Assistant(Entity):
    id: AssistantId
    owner_id: UserId
    type: AssistantType
    info: AssistantInfo
    instructions: Instructions
    is_deleted: bool

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def info_matches(self, name: str, description: str) -> bool:
        return self.info.name == name and self.info.description == description

    def instructions_matches(self, prompt: str) -> bool:
        return self.instructions.prompt == prompt

    def change_name(self, new_name: str) -> None:
        if self.info.name == new_name:
            return
        self.info = AssistantInfo(new_name, self.info.description)
        self._record_event(
            AssistantInfoChangedEvent(
                assistant_id=self.id.value,
                name=new_name,
                description=self.info.description,
            )
        )

    def change_description(self, new_description: str) -> None:
        if self.info.description == new_description:
            return
        self.info = AssistantInfo(self.info.name, new_description)
        self._record_event(
            AssistantInfoChangedEvent(
                assistant_id=self.id.value,
                name=self.info.name,
                description=new_description,
            )
        )

    def change_instructions(self, new_instructions: Instructions) -> None:
        self.instructions = new_instructions

    def delete(self) -> None:
        if self.type == AssistantType.SYSTEM:
            raise InvariantViolationError("System assistant cannot be deleted")
        if self.is_deleted:
            return
        self.is_deleted = True
        self._record_event(AssistantDeletedEvent(assistant_id=self.id.value))

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: AssistantId,
        owner_id: UserId,
        type: AssistantType,
        name: str,
        description: str,
        instructions: Instructions,
    ) -> Self:
        instance = cls(
            id=id,
            owner_id=owner_id,
            type=type,
            info=AssistantInfo(name, description),
            instructions=instructions,
            is_deleted=False,
        )
        instance._record_event(AssistantCreatedEvent(assistant_id=id.value))
        return instance
