from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.delete_chat_use_case import (
    DeleteChatCommand,
)
from luminary.chat.application.usecases.command.delete_chat_use_case import (
    DeleteChatUseCase,
)
from luminary.chat.domain.value_objects.chat_id import ChatId


@pytest.mark.asyncio
class TestDeleteChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()

        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
        )

        self.access_policy: Mock = Mock(spec=IChatAccessPolicy)
        self.repository: AsyncMock = AsyncMock(
            spec=IChatRepository,
            get_by_id=AsyncMock(return_value=self.chat),
        )

        self.command = DeleteChatCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
        )

        self.use_case = DeleteChatUseCase(
            repository=self.repository,
            access_policy=self.access_policy,
        )

    async def test_calls_repository_get_by_id_with_chat_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.get_by_id.assert_awaited_once_with(
            ChatId(self.chat_id)
        )

    async def test_calls_access_policy_with_user_and_chat(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.chat
        )

    async def test_calls_repository_save_with_soft_deleted_chat(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.save.assert_awaited_once_with(self.chat)
        assert self.chat.is_deleted

    async def test_raises_not_found_when_chat_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(
            ChatId(self.chat_id)
        )

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.chat.id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)
