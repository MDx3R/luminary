from dataclasses import dataclass, field
from typing import Self

from common.domain.interfaces.entity import Entity
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.events.events import (
    FolderAssistantChangedEvent,
    FolderChatAddedEvent,
    FolderChatRemovedEvent,
    FolderDeletedEvent,
    FolderEditorContentUpdatedEvent,
    FolderInfoChangedEvent,
    FolderSourceAddedEvent,
    FolderSourceRemovedEvent,
)
from luminary.folder.domain.value_objects.editor_content import EditorContent
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo
from luminary.source.domain.entity.source import SourceId


@dataclass
class Folder(Entity):
    id: FolderId
    owner_id: UserId
    info: FolderInfo
    assistant_id: AssistantId | None
    created_at: DateTime
    is_deleted: bool
    _chats: set[ChatId] = field(default_factory=set[ChatId])
    _sources: set[SourceId] = field(default_factory=set[SourceId])
    editor_content: EditorContent | None = None

    @property
    def chats(self) -> frozenset[ChatId]:
        return frozenset(self._chats)

    @property
    def sources(self) -> frozenset[SourceId]:
        return frozenset(self._sources)

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def change_name(self, name: str) -> None:
        self.change_info(FolderInfo(name, self.info.description))

    def change_description(self, description: str | None) -> None:
        self.change_info(FolderInfo(self.info.name, description))

    def change_info(self, info: FolderInfo) -> None:
        if self.info_matches(info):
            return

        self.info = info
        self._record_event(
            FolderInfoChangedEvent(
                folder_id=self.id.value, name=info.name, description=info.description
            )
        )

    def info_matches(self, info: FolderInfo) -> bool:
        return self.info == info

    def change_assistant(self, assistant_id: AssistantId) -> None:
        if self.assistant_matches(assistant_id):
            return

        self.assistant_id = assistant_id
        self._record_event(
            FolderAssistantChangedEvent(
                folder_id=self.id.value, assistant_id=assistant_id.value
            )
        )

    def remove_assistant(self) -> None:
        if self.assistant_matches(None):
            return

        self.assistant_id = None
        self._record_event(
            FolderAssistantChangedEvent(folder_id=self.id.value, assistant_id=None)
        )

    def assistant_matches(self, assistant_id: AssistantId | None) -> bool:
        return self.assistant_id == assistant_id

    def add_chat(self, chat_id: ChatId) -> None:
        if self.has_chat(chat_id):
            return

        self._chats.add(chat_id)
        self._record_event(
            FolderChatAddedEvent(folder_id=self.id.value, chat_id=chat_id.value)
        )

    def remove_chat(self, chat_id: ChatId) -> None:
        if not self.has_chat(chat_id):
            return

        self._chats.remove(chat_id)
        self._record_event(
            FolderChatRemovedEvent(folder_id=self.id.value, chat_id=chat_id.value)
        )

    def has_chat(self, chat_id: ChatId) -> bool:
        return chat_id in self.chats

    def add_source(self, source_id: SourceId) -> None:
        if self.has_source(source_id):
            return

        self._sources.add(source_id)
        self._record_event(
            FolderSourceAddedEvent(folder_id=self.id.value, source_id=source_id.value)
        )

    def remove_source(self, source_id: SourceId) -> None:
        if not self.has_source(source_id):
            return

        self._sources.remove(source_id)
        self._record_event(
            FolderSourceRemovedEvent(folder_id=self.id.value, source_id=source_id.value)
        )

    def has_source(self, source_id: SourceId) -> bool:
        return source_id in self._sources

    def editor_text_matches(self, text: str) -> bool:
        if not text.strip() and self.editor_content is None:
            return True
        if self.editor_content is None:
            return False
        return self.editor_content.text == text

    def update_editor_content(self, text: str, updated_at: DateTime) -> None:
        self.editor_content = EditorContent(text=text, updated_at=updated_at)
        self._record_event(FolderEditorContentUpdatedEvent(folder_id=self.id.value))

    def clear_editor_content(self) -> None:
        if self.editor_content is None:
            return

        self.editor_content = None
        self._record_event(FolderEditorContentUpdatedEvent(folder_id=self.id.value))

    def delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self._record_event(FolderDeletedEvent(folder_id=self.id.value))

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
            is_deleted=False,
        )
