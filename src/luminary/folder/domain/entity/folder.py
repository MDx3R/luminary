from dataclasses import dataclass, field
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass(frozen=True)
class FolderInfo:
    name: str
    description: str | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Folder name cannot be empty")


@dataclass
class Folder:
    folder_id: UUID
    user_id: UUID
    info: FolderInfo
    model_id: UUID
    assistant_id: UUID
    created_at: DateTime
    _chats: set[UUID] = field(default_factory=set[UUID])
    _sources: set[UUID] = field(default_factory=set[UUID])

    @property
    def chats(self) -> frozenset[UUID]:
        return frozenset(self._chats)

    @property
    def sources(self) -> frozenset[UUID]:
        return frozenset(self._sources)

    def change_name(self, name: str) -> None:
        self.info = FolderInfo(name, self.info.description)

    def change_description(self, description: str) -> None:
        self.info = FolderInfo(self.info.name, description)

    def change_model(self, model_id: UUID) -> None:
        self.model_id = model_id

    def change_assistant(self, assistant_id: UUID) -> None:
        self.assistant_id = assistant_id

    def add_chat(self, chat_id: UUID) -> None:
        self._chats.add(chat_id)

    def remove_chat(self, chat_id: UUID) -> None:
        self._chats.remove(chat_id)

    def add_source(self, source_id: UUID) -> None:
        self._sources.add(source_id)

    def remove_source(self, source_id: UUID) -> None:
        self._sources.remove(source_id)

    def has_source(self, source_id: UUID) -> bool:
        return source_id in self._sources

    def has_chat(self, chat_id: UUID) -> bool:
        return chat_id in self.chats

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        folder_id: UUID,
        user_id: UUID,
        name: str,
        description: str | None,
        model_id: UUID,
        assistant_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(
            folder_id=folder_id,
            info=FolderInfo(name=name, description=description),
            user_id=user_id,
            model_id=model_id,
            assistant_id=assistant_id,
            created_at=created_at,
        )
