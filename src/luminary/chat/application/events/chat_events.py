from dataclasses import dataclass
from uuid import UUID

from common.application.events.application_event import ApplicationEvent


@dataclass(frozen=True)
class ChatApplicationEvent(ApplicationEvent):
    chat_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.chat_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "chat"


@dataclass(frozen=True)
class ChatAddSourceRequestedEvent(ChatApplicationEvent):
    source_id: UUID


@dataclass(frozen=True)
class ChatRemoveSourceRequestedEvent(ChatApplicationEvent):
    source_id: UUID
