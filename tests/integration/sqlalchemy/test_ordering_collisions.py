import asyncio
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import (
    MakerSessionFactory,
)
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from tests.integration.sqlalchemy.utils import add_chat, add_folder

from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    ReorderChatsCommand,
)
from luminary.chat.application.policies.chat_access_policy import ChatAccessPolicy
from luminary.chat.application.usecases.command.reorder_chats_use_case import (
    ReorderChatsUseCase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.application.interfaces.usecases.command.reorder_folders_use_case import (
    ReorderFoldersCommand,
)
from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy
from luminary.folder.application.usecases.command.reorder_folders_use_case import (
    ReorderFoldersUseCase,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)


@pytest.mark.asyncio
async def test_concurrent_folder_reorders_keep_a_gap_for_next_insertion(maker) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    repository = FolderRepository(executor)
    use_case = ReorderFoldersUseCase(repository, FolderAccessPolicy())
    owner = uuid4()
    folders = [await add_folder(maker, owner_id=owner) for _ in range(5)]
    left, right = sorted(folders[:2], key=lambda folder: folder.order_key)
    await asyncio.gather(
        *[
            use_case.execute(
                ReorderFoldersCommand(
                    user_id=owner,
                    folder_id=folder.id.value,
                    previous_folder_id=left.id.value,
                    next_folder_id=right.id.value,
                )
            )
            for folder in folders[2:4]
        ]
    )
    neighbours = sorted(
        [await repository.get_by_id(folder.id) for folder in folders[2:4]],
        key=lambda folder: folder.order_key,
    )
    assert (
        left.order_key
        < neighbours[0].order_key
        < neighbours[1].order_key
        < right.order_key
    )
    await use_case.execute(
        ReorderFoldersCommand(
            user_id=owner,
            folder_id=folders[4].id.value,
            previous_folder_id=neighbours[0].id.value,
            next_folder_id=neighbours[1].id.value,
        )
    )
    key = (await repository.get_by_id(folders[4].id)).order_key
    assert neighbours[0].order_key < key < neighbours[1].order_key
    assert (await repository.get_by_id(left.id)).order_key == left.order_key
    assert (await repository.get_by_id(right.id)).order_key == right.order_key


@pytest.mark.asyncio
@pytest.mark.parametrize("in_folder", [False, True])
async def test_concurrent_chat_reorders_keep_a_gap_for_next_insertion(
    maker, in_folder: bool
) -> None:
    executor = QueryExecutor(UnitOfWork(MakerSessionFactory(maker)))
    repository = ChatRepository(executor)
    use_case = ReorderChatsUseCase(
        repository, FolderRepository(executor), FolderAccessPolicy(), ChatAccessPolicy()
    )
    owner = uuid4()
    folder = await add_folder(maker, owner_id=owner) if in_folder else None
    chats = [
        await add_chat(
            maker, user_id=owner, folder_id=folder.id.value if folder else None
        )
        for _ in range(5)
    ]
    left, right = sorted(chats[:2], key=lambda chat: chat.order_key)
    await asyncio.gather(
        *[
            use_case.execute(
                ReorderChatsCommand(
                    user_id=owner,
                    chat_id=chat.id.value,
                    previous_chat_id=left.id.value,
                    next_chat_id=right.id.value,
                )
            )
            for chat in chats[2:4]
        ]
    )
    neighbours = sorted(
        [await repository.get_by_id(chat.id) for chat in chats[2:4]],
        key=lambda chat: chat.order_key,
    )
    assert (
        left.order_key
        < neighbours[0].order_key
        < neighbours[1].order_key
        < right.order_key
    )
    await use_case.execute(
        ReorderChatsCommand(
            user_id=owner,
            chat_id=chats[4].id.value,
            previous_chat_id=neighbours[0].id.value,
            next_chat_id=neighbours[1].id.value,
        )
    )
    key = (await repository.get_by_id(chats[4].id)).order_key
    assert neighbours[0].order_key < key < neighbours[1].order_key
    assert (await repository.get_by_id(left.id)).order_key == left.order_key
    assert (await repository.get_by_id(right.id)).order_key == right.order_key
