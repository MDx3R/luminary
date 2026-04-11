from dataclasses import dataclass
from uuid import UUID

from common.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class AssistantEvent(DomainEvent):
    assistant_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.assistant_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "assistant"


@dataclass(frozen=True)
class AssistantCreatedEvent(AssistantEvent):
    pass


@dataclass(frozen=True)
class AssistantInfoChangedEvent(AssistantEvent):
    name: str
    description: str


@dataclass(frozen=True)
class AssistantDeletedEvent(AssistantEvent):
    pass
