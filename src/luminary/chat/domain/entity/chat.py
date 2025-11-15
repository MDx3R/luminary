from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.folder.domain.entity.folder import FolderId
from luminary.source.domain.entity.source import SourceId


@dataclass
class Chat:
    id: ChatId
    owner_id: UserId
    folder_id: FolderId | None  # TODO: Consider removing
    info: ChatInfo
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

    def change_name(self, new_name: str) -> None:
        self.info = ChatInfo(new_name)

    def change_system_prompt(self, new_system_prompt: str) -> None:
        self.settings = ChatSettings(
            self.settings.model_id,
            new_system_prompt,
            self.settings.max_context_messages,
        )

    def change_settings(self, new_settings: ChatSettings) -> None:
        self.settings = new_settings

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: ChatId,
        owner_id: UserId,
        folder_id: FolderId | None,
        name: str,
        settings: ChatSettings,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            folder_id=folder_id,
            info=ChatInfo(name=name),
            settings=settings,
            created_at=created_at,
        )
