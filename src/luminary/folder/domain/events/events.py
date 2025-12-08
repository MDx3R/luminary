from dataclasses import dataclass
from uuid import UUID

from common.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class FolderEvent(DomainEvent):
    folder_id: UUID

    @property
    def aggregate_id(self) -> UUID:
        return self.folder_id

    @classmethod
    def aggregate_type(cls) -> str:
        return "folder"


@dataclass(frozen=True)
class FolderChatAddedEvent(FolderEvent):
    chat_id: UUID


@dataclass(frozen=True)
class FolderChatRemovedEvent(FolderEvent):
    chat_id: UUID


@dataclass(frozen=True)
class FolderSourceAddedEvent(FolderEvent):
    source_id: UUID


@dataclass(frozen=True)
class FolderSourceRemovedEvent(FolderEvent):
    source_id: UUID


@dataclass(frozen=True)
class FolderAssistantChangedEvent(FolderEvent):
    assistant_id: UUID | None


@dataclass(frozen=True)
class FolderInfoChangedEvent(FolderEvent):
    name: str
    description: str | None
