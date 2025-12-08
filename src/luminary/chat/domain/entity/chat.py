from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


@dataclass
class Chat:
    id: ChatId
    owner_id: UserId
    folder_id: FolderId | None  # TODO: Consider removing
    info: ChatInfo
    assistant_id: AssistantId | None
    settings: ChatSettings
    created_at: DateTime
    _sources: set[SourceId] = field(default_factory=set[SourceId])

    @property
    def sources(self) -> Sequence[SourceId]:
        return list(self._sources)

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def add_source(self, source_id: SourceId) -> None:
        self._sources.add(source_id)

    def remove_source(self, source_id: SourceId) -> None:
        self._sources.remove(source_id)

    def has_source(self, source_id: SourceId) -> bool:
        return source_id in self._sources

    def change_name(self, new_name: str) -> None:
        self.info = ChatInfo(new_name)

    def change_settings(self, new_settings: ChatSettings) -> None:
        self.settings = new_settings

    def assistant_matches(self, assistant_id: AssistantId | None) -> bool:
        return self.assistant_id == assistant_id

    def apply_assistant(self, assistant_id: AssistantId) -> None:
        self.assistant_id = assistant_id

    def remove_assistant(self) -> None:
        self.assistant_id = None

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: ChatId,
        owner_id: UserId,
        folder_id: FolderId | None,
        name: str,
        assistant_id: AssistantId | None,
        settings: ChatSettings,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            folder_id=folder_id,
            info=ChatInfo(name=name),
            assistant_id=assistant_id,
            settings=settings,
            created_at=created_at,
        )
