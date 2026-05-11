from dataclasses import dataclass, field
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.interfaces.entity import Entity
from common.domain.value_objects.id import EntityId, UserId

from luminary.assistant.domain.enums import AssistantType
from luminary.assistant.domain.events.events import (
    AssistantClonedEvent,
    AssistantCreatedEvent,
    AssistantDeletedEvent,
    AssistantInfoChangedEvent,
    AssistantPublishedEvent,
)


MAX_TAG_LENGTH = 50
MAX_TAGS_COUNT = 20


def _validate_tags(tags: list[str]) -> None:
    if len(tags) > MAX_TAGS_COUNT:
        raise InvariantViolationError(
            f"Assistant cannot have more than {MAX_TAGS_COUNT} tags"
        )
    for tag in tags:
        if not tag.strip():
            raise InvariantViolationError("Tag cannot be empty")
        if len(tag) > MAX_TAG_LENGTH:
            raise InvariantViolationError(
                f"Tag cannot exceed {MAX_TAG_LENGTH} characters"
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
    owner_id: UserId | None
    type: AssistantType
    info: AssistantInfo
    instructions: Instructions
    is_deleted: bool
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.owner_id is None and self.type != AssistantType.SYSTEM:
            raise InvariantViolationError("Only system assistants can have no owner")

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def info_matches(self, name: str, description: str) -> bool:
        return self.info.name == name and self.info.description == description

    def tags_matches(self, tags: list[str]) -> bool:
        return self.tags == tags

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

    def change_tags(self, new_tags: list[str]) -> None:
        _validate_tags(new_tags)
        self.tags = new_tags

    def publish(self) -> None:
        if self.type != AssistantType.PERSONAL:
            raise InvariantViolationError("Only personal assistants can be published")
        self.type = AssistantType.PUBLIC
        self._record_event(AssistantPublishedEvent(assistant_id=self.id.value))

    @classmethod
    def clone(
        cls,
        source: "Assistant",
        new_id: "AssistantId",
        new_owner_id: UserId,
    ) -> "Assistant":
        instance = cls(
            id=new_id,
            owner_id=new_owner_id,
            type=AssistantType.PERSONAL,
            info=source.info,
            instructions=source.instructions,
            is_deleted=False,
            tags=list(source.tags),
        )
        instance._record_event(
            AssistantClonedEvent(
                assistant_id=new_id.value,
                source_assistant_id=source.id.value,
            )
        )
        return instance

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
        owner_id: UserId | None,
        type: AssistantType,
        name: str,
        description: str,
        instructions: Instructions,
        tags: list[str] | None = None,
    ) -> Self:
        resolved_tags = tags or []
        _validate_tags(resolved_tags)
        instance = cls(
            id=id,
            owner_id=owner_id,
            type=type,
            info=AssistantInfo(name, description),
            instructions=instructions,
            is_deleted=False,
            tags=resolved_tags,
        )
        instance._record_event(AssistantCreatedEvent(assistant_id=id.value))
        return instance
