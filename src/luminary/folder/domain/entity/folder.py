from dataclasses import dataclass, field
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.source.domain.entity.source import SourceId


@dataclass(frozen=True)
class FolderInfo:
    name: str
    description: str | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Folder name cannot be empty")


@dataclass(frozen=True)
class FolderId(EntityId): ...


@dataclass
class Folder:
    id: FolderId
    owner_id: UserId
    info: FolderInfo
    assistant_id: AssistantId | None
    created_at: DateTime
    _chats: set[ChatId] = field(default_factory=set[ChatId])
    _sources: set[SourceId] = field(default_factory=set[SourceId])

    @property
    def chats(self) -> frozenset[ChatId]:
        return frozenset(self._chats)

    @property
    def sources(self) -> frozenset[SourceId]:
        return frozenset(self._sources)

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def change_name(self, name: str) -> None:
        self.info = FolderInfo(name, self.info.description)

    def change_description(self, description: str) -> None:
        self.info = FolderInfo(self.info.name, description)

    def assistant_matches(self, assistant_id: AssistantId | None) -> bool:
        return self.assistant_id == assistant_id

    def change_assistant(self, assistant_id: AssistantId) -> None:
        self.assistant_id = assistant_id

    def remove_assistant(self) -> None:
        self.assistant_id = None

    def add_chat(self, chat_id: ChatId) -> None:
        self._chats.add(chat_id)

    def remove_chat(self, chat_id: ChatId) -> None:
        self._chats.remove(chat_id)

    def add_source(self, source_id: SourceId) -> None:
        self._sources.add(source_id)

    def remove_source(self, source_id: SourceId) -> None:
        self._sources.remove(source_id)

    def has_source(self, source_id: SourceId) -> bool:
        return source_id in self._sources

    def has_chat(self, chat_id: ChatId) -> bool:
        return chat_id in self.chats

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: FolderId,
        owner_id: UserId,
        name: str,
        description: str | None,
        assistant_id: AssistantId | None,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            info=FolderInfo(name=name, description=description),
            owner_id=owner_id,
            assistant_id=assistant_id,
            created_at=created_at,
        )
