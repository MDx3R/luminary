from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

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
        # Arrange
        user_id = uuid4()
        chat_id_1 = uuid4()
        chat_id_2 = uuid4()
        created_at_1 = datetime.now(UTC)
        updated_at_1 = datetime.now(UTC)
        created_at_2 = datetime.now(UTC)
        updated_at_2 = datetime.now(UTC)

        expected_chats = [
            ChatListItemDTO(
                chat_id=chat_id_1,
                name="Chat 1",
                created_at=created_at_1,
                updated_at=updated_at_1,
            ),
            ChatListItemDTO(
                chat_id=chat_id_2,
                name="Chat 2",
                created_at=created_at_2,
                updated_at=updated_at_2,
            ),
        ]

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert result == expected_chats

        chat_read_repository.get_by_user_id.assert_awaited_once_with(user_id)
        assert chat_read_repository.get_by_folder_id.call_count == 0

    async def test_execute_returns_folder_chats_when_folder_specified(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        folder_id = uuid4()
        chat_id = uuid4()
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        expected_chats = [
            ChatListItemDTO(
                chat_id=chat_id,
                name="Folder Chat",
                created_at=created_at,
                updated_at=updated_at,
            ),
        ]

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_folder_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id, folder_id=folder_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert result == expected_chats

        chat_read_repository.get_by_folder_id.assert_awaited_once_with(folder_id)
        assert chat_read_repository.get_by_user_id.call_count == 0

    async def test_execute_returns_empty_sequence_when_user_has_no_chats(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        expected_chats: list[ChatListItemDTO] = []

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert result == expected_chats

        chat_read_repository.get_by_user_id.assert_awaited_once_with(user_id)

    async def test_execute_calls_correct_repository_method_based_on_folder_id(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        folder_id = uuid4()

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = []
        chat_read_repository.get_by_folder_id.return_value = []

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)

        # Act - без folder_id
        query_without_folder = GetUserChatsQuery(user_id=user_id)
        await use_case.execute(query_without_folder)

        # Assert
        assert chat_read_repository.get_by_user_id.call_count == 1
        assert chat_read_repository.get_by_folder_id.call_count == 0

        # Reset
        chat_read_repository.reset_mock()

        query_with_folder = GetUserChatsQuery(
            user_id=user_id,
            folder_id=folder_id,
        )
        await use_case.execute(query_with_folder)

        # Assert
        assert chat_read_repository.get_by_folder_id.call_count == 1
        assert chat_read_repository.get_by_user_id.call_count == 0

    async def test_execute_returns_multiple_chats_with_correct_order(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()

        expected_chats = [
            ChatListItemDTO(
                chat_id=uuid4(),
                name="Chat 1",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            ChatListItemDTO(
                chat_id=uuid4(),
                name="Chat 2",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            ChatListItemDTO(
                chat_id=uuid4(),
                name="Chat 3",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        expected_chats_count = 3
        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_user_id.return_value = expected_chats

        use_case = GetUserChatsUseCase(chat_read_repository=chat_read_repository)
        query = GetUserChatsQuery(user_id=user_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert result == expected_chats
        assert len(result) == expected_chats_count
