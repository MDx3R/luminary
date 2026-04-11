from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat, make_message

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.cancel_message_use_case import (
    CancelMessageCommand,
)
from luminary.chat.application.usecases.command.cancel_message_use_case import (
    CancelMessageUseCase,
)
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId


@pytest.mark.asyncio
class TestCancelMessageUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.message_id = uuid4()

        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
        )
        self.message = make_message(
            message_id=self.message_id,
            chat_id=self.chat_id,
            role=Author.ASSISTANT,
            status=MessageStatus.STREAMING,
        )

        self.chat_repository: AsyncMock = AsyncMock(
            spec=IChatRepository,
            get_by_id=AsyncMock(return_value=self.chat),
        )
        self.message_repository: AsyncMock = AsyncMock(
            spec=IMessageRepository,
            get_by_id=AsyncMock(return_value=self.message),
        )
        self.access_policy: Mock = Mock(spec=IChatAccessPolicy)

        self.command = CancelMessageCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
            message_id=self.message_id,
        )

        self.use_case = CancelMessageUseCase(
            chat_repository=self.chat_repository,
            message_repository=self.message_repository,
            access_policy=self.access_policy,
        )

    async def test_calls_chat_repository_get_by_id_with_chat_id(self) -> None:
        await self.use_case.execute(self.command)

        self.chat_repository.get_by_id.assert_awaited_once_with(
            ChatId(self.chat_id)
        )

    async def test_calls_access_policy_with_user_and_chat(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.chat
        )

    async def test_calls_message_repository_get_by_id_with_message_id(
        self,
    ) -> None:
        await self.use_case.execute(self.command)

        self.message_repository.get_by_id.assert_awaited_once_with(
            MessageId(self.message_id)
        )

    async def test_cancels_message_and_saves(self) -> None:
        await self.use_case.execute(self.command)

        self.message_repository.save.assert_awaited_once_with(self.message)
        assert self.message.status == MessageStatus.CANCELLED

    async def test_raises_when_message_not_in_chat(self) -> None:
        other_chat_id = uuid4()
        self.message = make_message(
            message_id=self.message_id,
            chat_id=other_chat_id,
            role=Author.ASSISTANT,
            status=MessageStatus.STREAMING,
        )
        self.message_repository.get_by_id.return_value = self.message

        with pytest.raises(ValueError, match="does not belong"):
            await self.use_case.execute(self.command)

    async def test_raises_not_found_when_chat_not_exists(self) -> None:
        self.chat_repository.get_by_id.side_effect = NotFoundError(
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
