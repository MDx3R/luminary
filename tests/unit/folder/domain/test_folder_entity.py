from datetime import UTC, datetime
from uuid import uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.events.events import (
    FolderAssistantChangedEvent,
    FolderChatAddedEvent,
    FolderChatRemovedEvent,
    FolderEditorContentUpdatedEvent,
    FolderInfoChangedEvent,
    FolderSourceAddedEvent,
    FolderSourceRemovedEvent,
)
from luminary.folder.domain.value_objects.editor_content import EditorContent
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo
from luminary.source.domain.entity.source import SourceId


def _now() -> DateTime:
    return DateTime(datetime.now(UTC))


class TestFolderEntity:
    def test_create_success(self) -> None:
        folder_id = FolderId(uuid4())
        owner_id = UserId(uuid4())
        created_at = _now()

        folder = Folder.create(
            id=folder_id,
            owner_id=owner_id,
            name="My Folder",
            description="Desc",
            assistant_id=None,
            created_at=created_at,
        )

        assert folder.id == folder_id
        assert folder.owner_id == owner_id
        assert folder.info.name == "My Folder"
        assert folder.info.description == "Desc"
        assert folder.assistant_id is None
        assert folder.created_at == created_at
        assert len(folder.chats) == 0
        assert len(folder.sources) == 0
        assert folder.editor_content is None

    def test_is_owned_by(self) -> None:
        owner_id = UserId(uuid4())
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=owner_id,
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        assert folder.is_owned_by(owner_id) is True
        assert folder.is_owned_by(UserId(uuid4())) is False

    def test_change_info_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("Old", "OldDesc"),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        folder.change_info(FolderInfo("New", "NewDesc"))
        assert folder.info.name == "New"
        assert folder.info.description == "NewDesc"
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderInfoChangedEvent)

    def test_change_info_idempotent_when_same(self) -> None:
        info = FolderInfo("Same", "SameDesc")
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=info,
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        folder.change_info(info)
        assert len(folder.events) == 0

    def test_change_assistant_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        asst_id = AssistantId(uuid4())
        folder.change_assistant(asst_id)
        assert folder.assistant_id == asst_id
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderAssistantChangedEvent)

    def test_remove_assistant_emits_event(self) -> None:
        asst_id = AssistantId(uuid4())
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=asst_id,
            created_at=_now(),
            is_deleted=False,
        )
        folder.remove_assistant()
        assert folder.assistant_id is None
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderAssistantChangedEvent)
        assert folder.events[0].assistant_id is None

    def test_remove_assistant_idempotent_when_already_none(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        folder.remove_assistant()
        assert len(folder.events) == 0

    def test_add_chat_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        chat_id = ChatId(uuid4())
        folder.add_chat(chat_id)
        assert folder.has_chat(chat_id)
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderChatAddedEvent)

    def test_add_chat_idempotent(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        chat_id = ChatId(uuid4())
        folder.add_chat(chat_id)
        folder.add_chat(chat_id)
        assert len(folder.events) == 1

    def test_remove_chat_emits_event(self) -> None:
        chat_id = ChatId(uuid4())
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
            _chats={chat_id},
        )
        folder.remove_chat(chat_id)
        assert not folder.has_chat(chat_id)
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderChatRemovedEvent)

    def test_add_source_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        source_id = SourceId(uuid4())
        folder.add_source(source_id)
        assert folder.has_source(source_id)
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderSourceAddedEvent)

    def test_remove_source_emits_event(self) -> None:
        source_id = SourceId(uuid4())
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
            _sources={source_id},
        )
        folder.remove_source(source_id)
        assert not folder.has_source(source_id)
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderSourceRemovedEvent)

    def test_update_editor_content_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        updated_at = _now()
        folder.update_editor_content("# Hello", updated_at)
        assert folder.editor_content is not None
        assert folder.editor_content.text == "# Hello"
        assert folder.editor_content.updated_at == updated_at
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderEditorContentUpdatedEvent)

    def test_clear_editor_content_emits_event(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            editor_content=EditorContent(text="x", updated_at=_now()),
            is_deleted=False,
        )
        folder.clear_editor_content()
        assert folder.editor_content is None
        assert len(folder.events) == 1
        assert isinstance(folder.events[0], FolderEditorContentUpdatedEvent)

    def test_clear_editor_content_idempotent_when_already_none(self) -> None:
        folder = Folder(
            id=FolderId(uuid4()),
            owner_id=UserId(uuid4()),
            info=FolderInfo("F", None),
            assistant_id=None,
            created_at=_now(),
            is_deleted=False,
        )
        folder.clear_editor_content()
        assert len(folder.events) == 0
