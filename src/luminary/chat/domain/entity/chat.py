from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self

from common.domain.interfaces.entity import Entity
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.events.events import (
    ChatAssistantChangedEvent,
    ChatDeletedEvent,
    ChatNameChangedEvent,
    ChatSettingsChangedEvent,
    ChatSourceAddedEvent,
    ChatSourceRemovedEvent,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


@dataclass
class Chat(Entity):
    id: ChatId
    owner_id: UserId
    folder_id: FolderId | None
    info: ChatInfo
    assistant_id: AssistantId | None
    settings: ChatSettings
    created_at: DateTime
    is_deleted: bool
    _sources: set[SourceId] = field(default_factory=set[SourceId])

    @property
    def sources(self) -> Sequence[SourceId]:
        return list(self._sources)

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def is_standalone(self) -> bool:
        return self.folder_id is None

    def add_source(self, source_id: SourceId) -> None:
        if self.has_source(source_id):
            return
        self._sources.add(source_id)
        self._record_event(
            ChatSourceAddedEvent(chat_id=self.id.value, source_id=source_id.value)
        )

    def remove_source(self, source_id: SourceId) -> None:
        if not self.has_source(source_id):
            return
        self._sources.remove(source_id)
        self._record_event(
            ChatSourceRemovedEvent(chat_id=self.id.value, source_id=source_id.value)
        )

    def has_source(self, source_id: SourceId) -> bool:
        return source_id in self._sources

    def name_matches(self, name: str) -> bool:
        return self.info.name == name

    def settings_matches(self, settings: ChatSettings) -> bool:
        return self.settings == settings

    def change_name(self, new_name: str) -> None:
        if self.info.name == new_name:
            return
        self.info = ChatInfo(new_name)
        self._record_event(ChatNameChangedEvent(chat_id=self.id.value, name=new_name))

    def change_settings(self, new_settings: ChatSettings) -> None:
        if self.settings == new_settings:
            return
        self.settings = new_settings
        self._record_event(ChatSettingsChangedEvent(chat_id=self.id.value))

    def assistant_matches(self, assistant_id: AssistantId | None) -> bool:
        return self.assistant_id == assistant_id

    def apply_assistant(self, assistant_id: AssistantId) -> None:
        if self.assistant_matches(assistant_id):
            return
        self.assistant_id = assistant_id
        self._record_event(
            ChatAssistantChangedEvent(
                chat_id=self.id.value, assistant_id=assistant_id.value
            )
        )

    def remove_assistant(self) -> None:
        if self.assistant_matches(None):
            return
        self.assistant_id = None
        self._record_event(
            ChatAssistantChangedEvent(chat_id=self.id.value, assistant_id=None)
        )

    def delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self._record_event(
            ChatDeletedEvent(
                chat_id=self.id.value,
                folder_id=self.folder_id.value if self.folder_id else None,
            )
        )

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
            is_deleted=False,
        )
