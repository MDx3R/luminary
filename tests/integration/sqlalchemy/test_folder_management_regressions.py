import asyncio
from datetime import UTC, datetime, timedelta
from importlib import import_module
from uuid import UUID, uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from common.domain.value_objects.order_key import initial_order_key, order_key_between
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import (
    MakerSessionFactory,
)
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy import Connection, inspect, select, text, update
from sqlalchemy.ext.asyncio import AsyncEngine
from tests.integration.sqlalchemy.utils import add_chat, add_folder

from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatAssociation,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)


@pytest.mark.asyncio
async def test_migration_adds_nullable_keys_without_backfilling(
    engine: AsyncEngine,
) -> None:
    migration = import_module("migrations.versions.6d42f8c91b03_folder_management")

    def roundtrip(connection: Connection) -> None:
        with Operations.context(MigrationContext.configure(connection)):
            migration.downgrade()
            connection.execute(
                text(
                    "INSERT INTO folders (folder_id, owner_id, name, is_deleted) VALUES (:id, :owner, 'legacy', false)"
                ),
                {"id": uuid4(), "owner": uuid4()},
            )
            connection.execute(
                text(
                    "INSERT INTO chats (chat_id, owner_id, name, is_deleted) VALUES (:id, :owner, 'legacy', false)"
                ),
                {"id": uuid4(), "owner": uuid4()},
            )
            folder_before = connection.execute(
                text("SELECT folder_id, created_at, updated_at FROM folders")
            ).one()
            chat_before = connection.execute(
                text("SELECT chat_id, created_at, updated_at FROM chats")
            ).one()
            migration.upgrade()
            assert connection.execute(
                text("SELECT order_key, collapsed FROM folders")
            ).one() == (None, False)
            assert (
                connection.execute(text("SELECT order_key FROM chats")).scalar_one()
                is None
            )
            assert (
                connection.execute(
                    text("SELECT folder_id, created_at, updated_at FROM folders")
                ).one()
                == folder_before
            )
            assert (
                connection.execute(
                    text("SELECT chat_id, created_at, updated_at FROM chats")
                ).one()
                == chat_before
            )
            migration.downgrade()
            assert "order_key" not in {
                column["name"] for column in inspect(connection).get_columns("chats")
            }
            assert "collapsed" not in {
                column["name"] for column in inspect(connection).get_columns("folders")
            }
            migration.upgrade()

    async with engine.begin() as connection:
        await connection.run_sync(roundtrip)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", [ChatBase, FolderBase])
async def test_legacy_order_matches_python_without_updating_neighbours(
    maker, model
) -> None:
    id_column = model.chat_id if model is ChatBase else model.folder_id
    id_name = id_column.key
    created = datetime(2026, 1, 1, 12, 34, 56, 123456, tzinfo=UTC)
    ids = [UUID(int=1), UUID(int=2), UUID(int=3)]
    dates = [created, created, created + timedelta(microseconds=1)]
    owner = uuid4()
    async with maker.begin() as session:
        session.add_all(
            [
                model(
                    **{
                        id_name: entity_id,
                        "owner_id": owner,
                        "name": "legacy",
                        "created_at": date,
                        "order_key": None,
                    }
                )
                for entity_id, date in zip(ids, dates, strict=True)
            ]
        )
    async with maker() as session:
        rows = (
            await session.execute(
                select(id_column, model.position_key).order_by(model.position_key)
            )
        ).all()
        assert [row[0] for row in rows] == [ids[2], ids[0], ids[1]]
        assert dict(rows) == {
            entity_id: initial_order_key(date, entity_id)
            for entity_id, date in zip(ids, dates, strict=True)
        }
    new_key = order_key_between(rows[0][1], rows[1][1])
    async with maker.begin() as session:
        await session.execute(
            update(model).where(id_column == ids[1]).values(order_key=new_key)
        )
    async with maker() as session:
        assert (
            await session.scalars(select(id_column).order_by(model.position_key))
        ).all() == [ids[2], ids[1], ids[0]]
        assert dict(
            (await session.execute(select(id_column, model.order_key))).all()
        ) == {ids[0]: None, ids[1]: new_key, ids[2]: None}


@pytest.mark.asyncio
@pytest.mark.parametrize("model", [ChatBase, FolderBase])
async def test_fractional_keys_use_bytewise_collation(maker, model) -> None:
    id_name = "chat_id" if model is ChatBase else "folder_id"
    keys = ["a0a", "a0Z", "a0V", "Zz", "a0"]
    async with maker.begin() as session:
        session.add_all(
            [
                model(
                    **{
                        id_name: uuid4(),
                        "owner_id": uuid4(),
                        "name": "ordered",
                        "order_key": key,
                    }
                )
                for key in keys
            ]
        )
    async with maker() as session:
        assert (
            await session.scalars(
                select(model.position_key).order_by(model.position_key)
            )
        ).all() == sorted(keys)


@pytest.mark.asyncio
@pytest.mark.parametrize("commit", [True, False])
async def test_move_event_waits_for_committed_location(maker, commit: bool) -> None:
    owner = uuid4()
    folder = await add_folder(maker, owner_id=owner)
    chat = await add_chat(maker, user_id=owner)
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    repository = FolderRepository(executor)
    async with maker() as writer:
        await writer.execute(
            update(ChatBase)
            .where(ChatBase.chat_id == chat.id.value)
            .values(folder_id=folder.id.value)
        )
        task = asyncio.create_task(repository.move_chat_association(chat.id))
        try:
            _, pending = await asyncio.wait({task}, timeout=0.1)
            assert task in pending
            if commit:
                await writer.commit()
            else:
                await writer.rollback()
            await asyncio.wait_for(task, timeout=5)
        finally:
            await writer.rollback()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    async with maker() as session:
        links = (await session.scalars(select(FolderChatAssociation.folder_id))).all()
        assert links == ([folder.id.value] if commit else [])


@pytest.mark.asyncio
@pytest.mark.parametrize("commit", [True, False])
async def test_folder_delete_event_waits_for_commit(maker, commit: bool) -> None:
    folder = await add_folder(maker)
    chat = await add_chat(
        maker, user_id=folder.owner_id.value, folder_id=folder.id.value
    )
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    repository = ChatRepository(executor)
    async with maker() as writer:
        await writer.execute(
            update(FolderBase)
            .where(FolderBase.folder_id == folder.id.value)
            .values(is_deleted=True)
        )
        task = asyncio.create_task(repository.delete_by_folder(folder.id))
        try:
            _, pending = await asyncio.wait({task}, timeout=0.1)
            assert task in pending
            if commit:
                await writer.commit()
            else:
                await writer.rollback()
            await asyncio.wait_for(task, timeout=5)
        finally:
            await writer.rollback()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    async with maker() as session:
        assert (
            await session.scalars(
                select(ChatBase.is_deleted).where(ChatBase.chat_id == chat.id.value)
            )
        ).one() is commit


@pytest.mark.asyncio
@pytest.mark.parametrize("delete_chats_first", [True, False])
async def test_delayed_move_and_remove_events_keep_deleted_folder_links(
    maker, query_executor: QueryExecutor, delete_chats_first: bool
) -> None:
    folder = await add_folder(maker)
    chat = await add_chat(
        maker, user_id=folder.owner_id.value, folder_id=folder.id.value
    )
    folders = FolderRepository(query_executor)
    folder.add_chat(chat.id)
    folder.delete()
    await folders.save(folder)
    if delete_chats_first:
        await ChatRepository(query_executor).delete_by_folder(folder.id)
    await folders.move_chat_association(chat.id)
    await folders.clear_chat_association(folder.id, chat.id)
    async with maker() as session:
        assert (await session.scalars(select(FolderChatAssociation.chat_id))).all() == [
            chat.id.value
        ]
