from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
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
from luminary.chat.application.usecases.command.move_chat_use_case import (
    MoveChatUseCase,
)
from luminary.chat.application.usecases.command.reorder_chats_use_case import (
    ReorderChatsUseCase,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
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
    chat_repository.move_to_folder.assert_awaited_once_with(chat.id, target.id)
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
    chat_repository.move_to_folder.assert_awaited_once_with(chat.id, None)


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
    chat_repository.move_to_folder.assert_not_awaited()


@pytest.mark.asyncio
async def test_reorder_chats_rejects_missing_or_duplicate_ids() -> None:
    owner_id = uuid4()
    first, second = ChatId(uuid4()), ChatId(uuid4())
    chat_repository = AsyncMock(spec=IChatRepository)
    chat_repository.list_ids_by_location.return_value = [first, second]
    use_case = ReorderChatsUseCase(
        chat_repository,
        AsyncMock(spec=IFolderRepository),
        Mock(spec=IFolderAccessPolicy),
    )

    await use_case.execute(
        ReorderChatsCommand(owner_id, None, [second.value, first.value])
    )
    chat_repository.set_order.assert_awaited_once_with(
        UserId(owner_id), None, [second, first]
    )

    with pytest.raises(InvariantViolationError):
        await use_case.execute(
            ReorderChatsCommand(owner_id, None, [first.value, first.value])
        )
    assert chat_repository.set_order.await_count == 1


@pytest.mark.asyncio
async def test_reorder_chats_checks_folder_access() -> None:
    owner_id = uuid4()
    folder = make_folder(owner_id=owner_id)
    chat_repository = AsyncMock(spec=IChatRepository)
    chat_repository.list_ids_by_location.return_value = []
    folder_repository = AsyncMock(spec=IFolderRepository)
    folder_repository.get_by_id.return_value = folder
    folder_policy = Mock(spec=IFolderAccessPolicy)
    use_case = ReorderChatsUseCase(chat_repository, folder_repository, folder_policy)

    await use_case.execute(ReorderChatsCommand(owner_id, folder.id.value, []))

    folder_policy.assert_is_allowed.assert_called_once_with(UserId(owner_id), folder)
    chat_repository.list_ids_by_location.assert_awaited_once_with(
        UserId(owner_id), FolderId(folder.id.value)
    )
