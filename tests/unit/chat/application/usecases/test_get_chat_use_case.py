from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from tests.unit.chat.utils import make_chat

from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
    GetChatQuery,
)
from luminary.chat.application.usecases.query.get_chat_use_case import GetChatUseCase


@pytest.mark.asyncio
class TestGetChatUseCase:
    async def test_execute_returns_chat_dto_on_success(self) -> None:
        # Arrange
        user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()
        folder_id = uuid4()
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        chat_entity = make_chat(
            chat_id=chat_id,
            user_id=user_id,
            model_id=model_id,
            folder_id=folder_id,
        )

        expected_dto = ChatDTO(
            chat_id=chat_id,
            user_id=user_id,
            folder_id=folder_id,
            name="Test Chat",
            model_id=model_id,
            system_prompt="Test prompt",
            max_context_messages=10,
            created_at=created_at,
            updated_at=updated_at,
        )

        chat_read_repository = AsyncMock()
        chat_repository = AsyncMock()
        chat_access_policy = Mock(unsafe=True)

        chat_repository.get_by_id.return_value = chat_entity
        chat_read_repository.get_by_id.return_value = expected_dto
        chat_access_policy.assert_is_allowed.return_value = None

        use_case = GetChatUseCase(
            chat_read_repository=chat_read_repository,
            chat_repository=chat_repository,
            chat_access_policy=chat_access_policy,
        )

        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        # Act
        result = await use_case.execute(query)

        # Assert
        assert result == expected_dto

        chat_repository.get_by_id.assert_awaited_once_with(chat_id)
        chat_read_repository.get_by_id.assert_awaited_once_with(chat_id)

        assert chat_access_policy.assert_is_allowed.call_count == 1
        call_args = chat_access_policy.assert_is_allowed.call_args
        assert call_args[0][0] == user_id
        assert call_args[0][1] == chat_entity

    async def test_execute_raises_access_policy_error_when_user_has_no_access(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        other_user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()
        error_message = "Access denied"

        chat_entity = make_chat(
            chat_id=chat_id,
            user_id=other_user_id,
            model_id=model_id,
        )

        chat_read_repository = AsyncMock()
        chat_repository = AsyncMock()
        chat_access_policy = Mock(unsafe=True)

        chat_repository.get_by_id.return_value = chat_entity
        chat_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            chat_id, error_message
        )

        use_case = GetChatUseCase(
            chat_read_repository=chat_read_repository,
            chat_repository=chat_repository,
            chat_access_policy=chat_access_policy,
        )

        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        # Act & Assert
        with pytest.raises(AccessPolicyError, match=error_message):
            await use_case.execute(query)

        assert chat_read_repository.get_by_id.call_count == 0

    async def test_execute_raises_not_found_error_when_chat_not_exists(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()

        chat_entity = make_chat(
            chat_id=chat_id,
            user_id=user_id,
            model_id=model_id,
        )

        chat_read_repository = AsyncMock()
        chat_repository = AsyncMock()
        chat_access_policy = Mock(unsafe=True)

        chat_repository.get_by_id.return_value = chat_entity
        chat_read_repository.get_by_id.return_value = None
        chat_access_policy.assert_is_allowed.return_value = None

        use_case = GetChatUseCase(
            chat_read_repository=chat_read_repository,
            chat_repository=chat_repository,
            chat_access_policy=chat_access_policy,
        )

        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await use_case.execute(query)

    async def test_execute_checks_access_policy_before_reading_from_repo(
        self,
    ) -> None:
        # Arrange
        user_id = uuid4()
        other_user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()

        chat_entity = make_chat(
            chat_id=chat_id,
            user_id=other_user_id,
            model_id=model_id,
        )

        chat_read_repository = AsyncMock()
        chat_repository = AsyncMock()
        chat_access_policy = Mock(unsafe=True)

        chat_repository.get_by_id.return_value = chat_entity
        chat_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            chat_id, "Access denied"
        )

        use_case = GetChatUseCase(
            chat_read_repository=chat_read_repository,
            chat_repository=chat_repository,
            chat_access_policy=chat_access_policy,
        )

        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await use_case.execute(query)

        assert chat_read_repository.get_by_id.call_count == 0
