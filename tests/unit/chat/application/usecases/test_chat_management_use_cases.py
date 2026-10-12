from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat
from tests.unit.folder.utils import make_folder

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.move_chat_use_case import (
    MoveChatCommand,
)
from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    ReorderChatsCommand,
)
from luminary.chat.application.policies.chat_access_policy import ChatAccessPolicy
from luminary.chat.application.usecases.command.move_chat_use_case import (
    MoveChatUseCase,
)
from luminary.chat.application.usecases.command.reorder_chats_use_case import (
    ReorderChatsUseCase,
)
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
async def test_move_chat_keeps_own_sources_and_checks_target_access() -> None:
    owner_id = uuid4()
    target = make_folder(owner_id=owner_id)
    chat = make_chat(user_id=owner_id)
    source_id = SourceId(uuid4())
    chat.add_source(source_id)
    chat_repository = AsyncMock(spec=IChatRepository)
    chat_repository.get_by_id.return_value = chat
    folder_repository = AsyncMock(spec=IFolderRepository)
    folder_repository.get_by_id.return_value = target
    chat_policy = Mock(spec=IChatAccessPolicy)
    folder_policy = Mock(spec=IFolderAccessPolicy)
    use_case = MoveChatUseCase(
        chat_repository, folder_repository, chat_policy, folder_policy
    )

    await use_case.execute(MoveChatCommand(owner_id, chat.id.value, target.id.value))

    folder_policy.assert_is_allowed.assert_called_once_with(UserId(owner_id), target)
    chat_repository.save.assert_awaited_once_with(chat)
    assert chat.folder_id == target.id
    assert source_id in chat.sources


@pytest.mark.asyncio
async def test_move_chat_to_root_does_not_load_a_folder() -> None:
    owner_id = uuid4()
    chat = make_chat(user_id=owner_id, folder_id=uuid4())
    chat_repository = AsyncMock(spec=IChatRepository)
    chat_repository.get_by_id.return_value = chat
    folder_repository = AsyncMock(spec=IFolderRepository)
    use_case = MoveChatUseCase(
        chat_repository,
        folder_repository,
        Mock(spec=IChatAccessPolicy),
        Mock(spec=IFolderAccessPolicy),
    )

    await use_case.execute(MoveChatCommand(owner_id, chat.id.value, None))

    folder_repository.get_by_id.assert_not_awaited()
    chat_repository.save.assert_awaited_once_with(chat)
    assert chat.folder_id is None


@pytest.mark.asyncio
async def test_move_chat_rejects_inaccessible_target() -> None:
    owner_id = uuid4()
    chat = make_chat(user_id=owner_id)
    chat_repository = AsyncMock(spec=IChatRepository)
    chat_repository.get_by_id.return_value = chat
    folder_repository = AsyncMock(spec=IFolderRepository)
    folder_repository.get_by_id.return_value = make_folder(owner_id=uuid4())
    folder_policy = Mock(spec=IFolderAccessPolicy)
    folder_policy.assert_is_allowed.side_effect = AccessPolicyError(
        folder_repository.get_by_id.return_value.id, "Access denied"
    )
    use_case = MoveChatUseCase(
        chat_repository,
        folder_repository,
        Mock(spec=IChatAccessPolicy),
        folder_policy,
    )

    with pytest.raises(AccessPolicyError):
        await use_case.execute(MoveChatCommand(owner_id, chat.id.value, uuid4()))
    chat_repository.save.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("location", [None, uuid4()])
async def test_move_chat_to_same_location_is_noop(location) -> None:
    chat = make_chat(folder_id=location)
    chats, folders = AsyncMock(spec=IChatRepository), AsyncMock(spec=IFolderRepository)
    chats.get_by_id.return_value = chat
    folders.get_by_id.return_value = make_folder(owner_id=chat.owner_id.value)
    await MoveChatUseCase(
        chats, folders, ChatAccessPolicy(), FolderAccessPolicy()
    ).execute(MoveChatCommand(chat.owner_id.value, chat.id.value, location))
    chats.save.assert_not_awaited()
    assert not chat.events


@pytest.mark.asyncio
@pytest.mark.parametrize("location", [None, uuid4()])
@pytest.mark.parametrize("placement", ["start", "middle", "end"])
async def test_reorder_chats_saves_only_moved_chat(location, placement) -> None:
    owner_id = uuid4()
    first = make_chat(user_id=owner_id, folder_id=location)
    second = make_chat(user_id=owner_id, folder_id=location)
    moved = make_chat(user_id=owner_id, folder_id=location)
    first.change_order("a0")
    second.change_order("a1")
    chat_repository = AsyncMock(spec=IChatRepository)
    chats = {chat.id: chat for chat in (first, second, moved)}
    chat_repository.get_by_id.side_effect = chats.__getitem__
    folder_repository = AsyncMock(spec=IFolderRepository)
    folder_repository.get_by_id.return_value = make_folder(owner_id=owner_id)
    use_case = ReorderChatsUseCase(
        chat_repository, folder_repository, FolderAccessPolicy(), ChatAccessPolicy()
    )
    previous = first if placement != "start" else None
    following = second if placement != "end" else None
    await use_case.execute(
        ReorderChatsCommand(
            owner_id,
            moved.id.value,
            previous.id.value if previous else None,
            following.id.value if following else None,
        )
    )
    chat_repository.save.assert_awaited_once_with(moved)
    assert first.order_key == "a0"
    assert second.order_key == "a1"
    assert previous is None or previous.order_key < moved.order_key
    assert following is None or moved.order_key < following.order_key


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    ["self", "duplicate", "reversed", "other-owner", "other-folder", "missing"],
)
async def test_reorder_chats_rejects_invalid_neighbours(invalid) -> None:
    owner_id = uuid4()
    moved = make_chat(user_id=owner_id)
    neighbour = make_chat(user_id=owner_id)
    next_chat = make_chat(user_id=owner_id)
    neighbour.change_order("a0")
    next_chat.change_order("a1")
    previous_id, next_id = neighbour.id.value, next_chat.id.value
    if invalid == "self":
        previous_id = moved.id.value
    elif invalid == "duplicate":
        next_id = previous_id
    elif invalid == "reversed":
        previous_id, next_id = next_id, previous_id
    elif invalid == "other-owner":
        neighbour.owner_id = UserId(uuid4())
    elif invalid == "other-folder":
        neighbour.folder_id = FolderId(uuid4())
    chat_repository = AsyncMock(spec=IChatRepository)
    chats = {chat.id: chat for chat in (moved, neighbour, next_chat)}
    chat_repository.get_by_id.side_effect = chats.__getitem__
    if invalid == "missing":
        chat_repository.get_by_id.side_effect = [moved, NotFoundError(neighbour.id)]
    use_case = ReorderChatsUseCase(
        chat_repository,
        AsyncMock(spec=IFolderRepository),
        FolderAccessPolicy(),
        ChatAccessPolicy(),
    )
    with pytest.raises((InvariantViolationError, AccessPolicyError, NotFoundError)):
        await use_case.execute(
            ReorderChatsCommand(owner_id, moved.id.value, previous_id, next_id)
        )
    chat_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_reorder_chat_rejects_inaccessible_chat() -> None:
    repository = AsyncMock(spec=IChatRepository)
    chat = make_chat()
    repository.get_by_id.return_value = chat
    use_case = ReorderChatsUseCase(
        repository,
        AsyncMock(spec=IFolderRepository),
        FolderAccessPolicy(),
        ChatAccessPolicy(),
    )
    with pytest.raises(AccessPolicyError):
        await use_case.execute(ReorderChatsCommand(uuid4(), chat.id.value))
    repository.save.assert_not_awaited()
