from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import (
    MakerSessionFactory,
)
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy import select
from tests.integration.sqlalchemy.utils import add_chat, add_folder

from luminary.chat.domain.events.events import ChatMovedEvent
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.application.handlers.chat_moved_handler import (
    FolderChatMovedHandler,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatAssociation,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)
from luminary.source.domain.entity.source import SourceId


def change_scalar(folder: Folder, field: str) -> None:
    if field == "collapsed":
        folder.set_collapsed(True)
    elif field == "order":
        folder.change_order("a0V")
    elif field == "info":
        folder.change_name("Updated")
    elif field == "editor":
        folder.update_editor_content("Updated", folder.created_at)
    else:
        folder.delete()


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["collapsed", "order", "info", "editor", "delete"])
async def test_stale_folder_save_does_not_restore_moved_chat(maker, field: str) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    folders, chats = FolderRepository(executor), ChatRepository(executor)
    folder = await add_folder(maker)
    target = await add_folder(maker, owner_id=folder.owner_id.value)
    chat = await add_chat(
        maker, user_id=folder.owner_id.value, folder_id=folder.id.value
    )
    folder.add_chat(chat.id)
    await folders.save(folder)
    stale = await folders.get_by_id(folder.id)

    chat.move_to_folder(target.id)
    await chats.save(chat)
    await FolderChatMovedHandler(folders, chats, executor.uow).handle(
        ChatMovedEvent(
            chat_id=chat.id.value,
            previous_folder_id=folder.id.value,
            folder_id=target.id.value,
        )
    )
    change_scalar(stale, field)
    await folders.save(stale)

    async with maker() as session:
        assert (
            await session.scalars(select(FolderChatAssociation.folder_id))
        ).all() == [target.id.value]
    assert (await chats.get_by_id(chat.id)).folder_id == target.id


@pytest.mark.asyncio
async def test_stale_folder_save_preserves_new_links_and_removed_sources(maker) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    folders = FolderRepository(executor)
    folder = await add_folder(maker)
    source = SourceId(uuid4())
    folder.add_source(source)
    await folders.save(folder)
    stale = await folders.get_by_id(folder.id)
    current = await folders.get_by_id(folder.id)
    chat = await add_chat(
        maker, user_id=folder.owner_id.value, folder_id=folder.id.value
    )
    current.add_chat(chat.id)
    current.remove_source(source)
    await folders.save(current)

    stale.set_collapsed(True)
    await folders.save(stale)
    actual = await folders.get_by_id(folder.id)
    assert actual.collapsed
    assert actual.chats == {chat.id}
    assert not actual.sources


@pytest.mark.asyncio
async def test_independent_scalar_updates_do_not_overwrite_each_other(maker) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    folders = FolderRepository(executor)
    folder = await add_folder(maker)
    stale = await folders.get_by_id(folder.id)
    current = await folders.get_by_id(folder.id)
    current.change_name("Concurrent update")
    current.change_order("a1V")
    current.delete()
    await folders.save(current)
    stale.set_collapsed(True)
    await folders.save(stale)
    async with maker() as session:
        actual = (await session.scalars(select(FolderBase))).one()
        assert actual.is_deleted
        assert actual.name == "Concurrent update"
        assert actual.order_key == "a1V"
        assert actual.collapsed


@pytest.mark.asyncio
async def test_association_changes_apply_deltas_not_stale_collections(maker) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    folders = FolderRepository(executor)
    folder = await add_folder(maker)
    left = await folders.get_by_id(folder.id)
    right = await folders.get_by_id(folder.id)
    first, second = SourceId(uuid4()), SourceId(uuid4())
    left.add_source(first)
    right.add_source(second)
    await folders.save(left)
    await folders.save(right)
    assert (await folders.get_by_id(folder.id)).sources == {first, second}
