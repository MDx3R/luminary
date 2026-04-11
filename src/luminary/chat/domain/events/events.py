from dataclasses import dataclass
from uuid import UUID

from common.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class ChatEvent(DomainEvent):
    chat_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.chat_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "chat"


@dataclass(frozen=True)
class ChatSourceAddedEvent(ChatEvent):
    source_id: UUID


@dataclass(frozen=True)
class ChatSourceRemovedEvent(ChatEvent):
    source_id: UUID


@dataclass(frozen=True)
class ChatNameChangedEvent(ChatEvent):
    name: str


@dataclass(frozen=True)
class ChatSettingsChangedEvent(ChatEvent):
    pass


@dataclass(frozen=True)
class ChatAssistantChangedEvent(ChatEvent):
    assistant_id: UUID | None


@dataclass(frozen=True)
class ChatDeletedEvent(ChatEvent):
    folder_id: UUID | None


# Message events (message aggregate, chat_id for context)
@dataclass(frozen=True)
class MessageEvent(DomainEvent):
    message_id: UUID
    chat_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.message_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "message"


@dataclass(frozen=True)
class MessageCompletedEvent(MessageEvent):
    tokens: int


@dataclass(frozen=True)
class MessageFailedEvent(MessageEvent):
    pass


@dataclass(frozen=True)
class MessageCancelledEvent(MessageEvent):
    pass
