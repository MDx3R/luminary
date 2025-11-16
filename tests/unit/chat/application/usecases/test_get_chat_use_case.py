from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from tests.unit.chat.utils import make_chat_dto

from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatQuery,
)
from luminary.chat.application.usecases.query.get_chat_use_case import GetChatUseCase


@pytest.mark.asyncio
class TestGetChatUseCase:
    async def test_execute_returns_chat_dto_on_success(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()

        expected_dto = make_chat_dto(chat_id=chat_id, user_id=user_id)

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_id_for_user.return_value = expected_dto

        use_case = GetChatUseCase(chat_read_repository=chat_read_repository)
        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        result = await use_case.execute(query)

        assert result == expected_dto
        chat_read_repository.get_by_id_for_user.assert_awaited_once_with(
            chat_id, user_id
        )

    async def test_execute_raises_not_found_error_when_user_has_no_access(
        self,
    ) -> None:
        user_id = uuid4()
        chat_id = uuid4()

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_id_for_user.return_value = None

        use_case = GetChatUseCase(chat_read_repository=chat_read_repository)
        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        with pytest.raises(NotFoundError):
            await use_case.execute(query)

    async def test_execute_raises_not_found_error_when_chat_not_exists(
        self,
    ) -> None:
        user_id = uuid4()
        chat_id = uuid4()

        chat_read_repository = AsyncMock()
        chat_read_repository.get_by_id_for_user.return_value = None

        use_case = GetChatUseCase(chat_read_repository=chat_read_repository)
        query = GetChatQuery(user_id=user_id, chat_id=chat_id)

        with pytest.raises(NotFoundError):
            await use_case.execute(query)
