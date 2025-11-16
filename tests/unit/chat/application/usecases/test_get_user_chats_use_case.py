from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from tests.unit.chat.utils import make_chat_list_item_dto

from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
    GetUserChatsQuery,
)
from luminary.chat.application.usecases.query.get_user_chats_use_case import (
    GetUserChatsUseCase,
)


@pytest.mark.asyncio
class TestGetUserChatsUseCase:
    async def test_execute_returns_user_chats_when_folder_not_specified(
        self,
    ) -> None:
        user_id = uuid4()

        expected_chats = [
            make_chat_list_item_dto(name="Chat 1"),
            make_chat_list_item_dto(name="Chat 2"),
        ]

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert result == expected_chats
        chat_read_repository.get_by_user_id.assert_awaited_once_with(user_id)
        assert chat_read_repository.get_by_folder_id_for_user.call_count == 0

    async def test_execute_returns_folder_chats_when_folder_specified(
        self,
    ) -> None:
        user_id = uuid4()
        folder_id = uuid4()

        expected_chats = [
            make_chat_list_item_dto(name="Folder Chat"),
        ]

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_folder_id_for_user.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id, folder_id=folder_id)

        result = await use_case.execute(query)

        assert result == expected_chats
        chat_read_repository.get_by_folder_id_for_user.assert_awaited_once_with(
            folder_id, user_id
        )
        assert chat_read_repository.get_by_user_id.call_count == 0

    async def test_execute_returns_empty_sequence_when_user_has_no_chats(
        self,
    ) -> None:
        user_id = uuid4()
        expected_chats: list[ChatListItemDTO] = []

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert result == expected_chats
        chat_read_repository.get_by_user_id.assert_awaited_once_with(user_id)

    async def test_execute_calls_correct_repository_method_based_on_folder_id(
        self,
    ) -> None:
        user_id = uuid4()
        folder_id = uuid4()

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = []
        chat_read_repository.get_by_folder_id_for_user.return_value = []

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)

        query_without_folder = GetUserChatsQuery(user_id=user_id)
        await use_case.execute(query_without_folder)

        assert chat_read_repository.get_by_user_id.call_count == 1
        assert chat_read_repository.get_by_folder_id_for_user.call_count == 0

        chat_read_repository.reset_mock()

        query_with_folder = GetUserChatsQuery(
            user_id=user_id,
            folder_id=folder_id,
        )
        await use_case.execute(query_with_folder)

        assert chat_read_repository.get_by_folder_id_for_user.call_count == 1
        assert chat_read_repository.get_by_user_id.call_count == 0

    async def test_execute_returns_multiple_chats_with_correct_order(
        self,
    ) -> None:
        user_id = uuid4()

        expected_chats = [
            make_chat_list_item_dto(name="Chat 1"),
            make_chat_list_item_dto(name="Chat 2"),
            make_chat_list_item_dto(name="Chat 3"),
        ]
        expected_chats_count = len(expected_chats)

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        result = await use_case.execute(query)

        assert result == expected_chats
        assert len(result) == expected_chats_count
