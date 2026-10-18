from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import (
    add_chat,
    add_file_source,
    add_folder,
    persist_chat,
)
from tests.unit.chat.utils import make_chat

from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    ReorderChatsCommand,
)
from luminary.chat.application.policies.chat_access_policy import ChatAccessPolicy
from luminary.chat.application.usecases.command.reorder_chats_use_case import (
    ReorderChatsUseCase,
)
from luminary.chat.domain.events.events import ChatMovedEvent
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.application.handlers.chat_moved_handler import (
    FolderChatMovedHandler,
)
from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_read_repository import (
    FolderReadRepository,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
class TestChatRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = ChatRepository(query_executor)

    async def test_get_by_id_success(self):
        # Arrange
        chat = await add_chat(self.maker)

        # Act
        result = await self.repository.get_by_id(chat.id)

        # Assert
        assert result.id == chat.id
        assert result.info.name == chat.info.name
        assert result.is_deleted is False

    async def test_get_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(ChatId(uuid4()))

    async def test_add_and_get(self):
        # Arrange
        chat = make_chat()

        # Act
        await self.repository.add(chat)
        loaded = await self.repository.get_by_id(chat.id)

        # Assert
        assert loaded.id == chat.id
        assert loaded.info.name == chat.info.name

    async def test_save_with_sources(self):
        # Arrange
        chat = await add_chat(self.maker)
        source_id = SourceId(uuid4())
        chat.add_source(source_id)

        # Act
        await self.repository.save(chat)
        loaded = await self.repository.get_by_id(chat.id)

        # Assert
        assert {s.value for s in loaded.sources} == {source_id.value}

    async def test_get_by_id_does_not_return_soft_deleted(self):
        # Arrange
        chat = await add_chat(self.maker)
        chat.delete()
        await self.repository.save(chat)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(chat.id)

    async def test_move_to_folder_and_root_preserves_chat_sources(
        self, query_executor: QueryExecutor
    ):
        owner_id = uuid4()
        source = await add_file_source(self.maker, owner_id=owner_id)
        chat = make_chat(user_id=owner_id)
        chat.add_source(source.id)
        await persist_chat(self.maker, chat)
        folder = await add_folder(self.maker, owner_id=owner_id)

        handler = FolderChatMovedHandler(
            FolderRepository(query_executor), self.repository, query_executor.uow
        )
        chat.move_to_folder(folder.id)
        await self.repository.save(chat)
        event = ChatMovedEvent(
            chat_id=chat.id.value, previous_folder_id=None, folder_id=folder.id.value
        )
        await handler.handle(event)
        await handler.handle(event)

        moved = await self.repository.get_by_id(chat.id)
        assert moved.folder_id == folder.id
        assert source.id in moved.sources
        detail = await FolderReadRepository(query_executor).get_by_id(
            folder.id.value, owner_id
        )
        assert [item.id for item in detail.chats] == [chat.id.value]

        moved.move_to_folder(None)
        await self.repository.save(moved)
        # Replaying an old move must synchronize the current location.
        await handler.handle(event)

        assert (await self.repository.get_by_id(chat.id)).folder_id is None
        detail = await FolderReadRepository(query_executor).get_by_id(
            folder.id.value, owner_id
        )
        assert detail.chats == []
        assert source.id in (await self.repository.get_by_id(chat.id)).sources

    async def test_move_between_folders_keeps_only_own_chat_sources(
        self, query_executor: QueryExecutor
    ):
        owner_id = uuid4()
        old_folder = await add_folder(self.maker, owner_id=owner_id)
        new_folder = await add_folder(self.maker, owner_id=owner_id)
        own_source = await add_file_source(self.maker, owner_id=owner_id)
        inherited_source = await add_file_source(self.maker, owner_id=owner_id)
        chat = await add_chat(
            self.maker, user_id=owner_id, folder_id=old_folder.id.value
        )
        chat.add_source(own_source.id)
        await self.repository.save(chat)
        folders = FolderRepository(query_executor)
        old_folder.add_chat(chat.id)
        old_folder.add_source(inherited_source.id)
        await folders.save(old_folder)

        chat.move_to_folder(new_folder.id)
        await self.repository.save(chat)
        # The old projection must already hide the chat before event processing.
        reader = FolderReadRepository(query_executor)
        assert (await reader.get_by_id(old_folder.id.value, owner_id)).chats == []
        await FolderChatMovedHandler(
            folders, self.repository, query_executor.uow
        ).handle(
            ChatMovedEvent(
                chat_id=chat.id.value,
                previous_folder_id=old_folder.id.value,
                folder_id=new_folder.id.value,
            )
        )

        moved = await self.repository.get_by_id(chat.id)
        assert set(moved.sources) == {own_source.id}
        assert (await folders.get_by_id(old_folder.id)).sources == frozenset(
            {inherited_source.id}
        )
        assert (await folders.get_by_id(old_folder.id)).chats == frozenset()
        assert [
            item.id
            for item in (await reader.get_by_id(new_folder.id.value, owner_id)).chats
        ] == [chat.id.value]

    async def test_reorder_saves_only_selected_chat(
        self, query_executor: QueryExecutor
    ):
        owner_id = uuid4()
        first = await add_chat(self.maker, user_id=owner_id)
        second = await add_chat(self.maker, user_id=owner_id)
        folder = await add_folder(self.maker, owner_id=owner_id)
        other = await add_chat(self.maker, user_id=owner_id, folder_id=folder.id.value)

        await ReorderChatsUseCase(
            self.repository,
            FolderRepository(query_executor),
            FolderAccessPolicy(),
            ChatAccessPolicy(),
        ).execute(
            ReorderChatsCommand(
                user_id=owner_id, chat_id=first.id.value, next_chat_id=second.id.value
            )
        )

        assert (await self.repository.get_by_id(first.id)).order_key < second.order_key
        assert (
            await self.repository.get_by_id(second.id)
        ).order_key == second.order_key
        assert (await self.repository.get_by_id(other.id)).order_key == other.order_key
