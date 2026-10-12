from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from tests.unit.chat.utils import make_chat
from tests.unit.folder.utils import make_folder

from luminary.chat.application.handlers.folder_deleted_handler import (
    ChatFolderDeletedHandler,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.events.events import (
    ChatDeletedEvent,
    ChatMovedEvent,
    ChatOrderChangedEvent,
)
from luminary.folder.application.handlers.chat_deleted_handler import (
    FolderChatDeletedHandler,
    FolderChatRemovedHandler,
)
from luminary.folder.application.handlers.chat_moved_handler import (
    FolderChatMovedHandler,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.events.events import (
    FolderChatRemovedEvent,
    FolderDeletedEvent,
    FolderOrderChangedEvent,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


def test_move_records_event_without_removing_chat_sources() -> None:
    chat = make_chat(folder_id=uuid4())
    source_id = SourceId(uuid4())
    chat.add_source(source_id)
    previous = chat.folder_id
    assert previous is not None
    target = FolderId(uuid4())
    chat.move_to_folder(target)
    assert chat.folder_id == target
    assert chat.events[-1] == ChatMovedEvent(
        chat_id=chat.id.value, previous_folder_id=previous.value, folder_id=target.value
    )
    assert source_id in chat.sources
    events = chat.events
    chat.move_to_folder(target)
    assert chat.events == events


def test_order_changes_record_events_once() -> None:
    chat, folder = make_chat(), make_folder()
    chat.change_order("a0")
    folder.change_order("a0")
    chat.change_order("a0")
    folder.change_order("a0")
    assert chat.events == [ChatOrderChangedEvent(chat_id=chat.id.value)]
    assert folder.events == [FolderOrderChangedEvent(folder_id=folder.id.value)]


@pytest.mark.asyncio
async def test_move_handler_synchronizes_chat_association() -> None:
    chat = make_chat()
    folders = AsyncMock(spec=IFolderRepository)
    handler = FolderChatMovedHandler(folders)
    event = ChatMovedEvent(
        chat_id=chat.id.value, previous_folder_id=uuid4(), folder_id=uuid4()
    )
    await handler.handle(event)
    folders.move_chat_association.assert_awaited_once_with(chat.id)


@pytest.mark.asyncio
async def test_folder_deleted_handler_deletes_chats_in_that_folder() -> None:
    repository = AsyncMock(spec=IChatRepository)
    folder_id = uuid4()
    await ChatFolderDeletedHandler(repository).handle(
        FolderDeletedEvent(folder_id=folder_id)
    )
    repository.delete_by_folder.assert_awaited_once_with(FolderId(folder_id))


@pytest.mark.asyncio
async def test_chat_deleted_handler_keeps_deleted_folder_links() -> None:
    repository = AsyncMock(spec=IFolderRepository)
    repository.get_by_id.side_effect = NotFoundError("folder")
    await FolderChatDeletedHandler(repository).handle(
        ChatDeletedEvent(chat_id=uuid4(), folder_id=uuid4())
    )
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_stale_remove_event_does_not_delete_moved_chat() -> None:
    chat = make_chat(folder_id=uuid4())
    repository = AsyncMock(spec=IChatRepository)
    repository.get_by_id.return_value = chat
    folders = AsyncMock(spec=IFolderRepository)
    await FolderChatRemovedHandler(repository, folders).handle(
        FolderChatRemovedEvent(folder_id=uuid4(), chat_id=chat.id.value)
    )
    assert not chat.is_deleted
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_remove_event_deletes_chat_and_clears_link() -> None:
    chat = make_chat(folder_id=uuid4())
    assert chat.folder_id is not None
    chats, folders = AsyncMock(spec=IChatRepository), AsyncMock(spec=IFolderRepository)
    chats.get_by_id.return_value = chat
    event = FolderChatRemovedEvent(
        folder_id=chat.folder_id.value, chat_id=chat.id.value
    )
    await FolderChatRemovedHandler(chats, folders).handle(event)
    assert chat.is_deleted
    chats.save.assert_awaited_once_with(chat)
    folders.clear_chat_association.assert_awaited_once_with(chat.folder_id, chat.id)


@pytest.mark.asyncio
async def test_remove_event_clears_link_when_chat_is_already_deleted() -> None:
    chats, folders = AsyncMock(spec=IChatRepository), AsyncMock(spec=IFolderRepository)
    chats.get_by_id.side_effect = NotFoundError("chat")
    event = FolderChatRemovedEvent(folder_id=uuid4(), chat_id=uuid4())
    await FolderChatRemovedHandler(chats, folders).handle(event)
    chats.save.assert_not_awaited()
    folders.clear_chat_association.assert_awaited_once()
