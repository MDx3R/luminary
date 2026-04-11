from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat, make_chat_settings

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    SendMessageCommand,
)
from luminary.chat.application.usecases.command.send_message_use_case import (
    SendMessageUseCase,
)
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId


@pytest.mark.asyncio
class TestSendMessageUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.chat_id = uuid4()
        self.content = "Hello"

        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
            settings=make_chat_settings(max_context_messages=5),
        )
        now = DateTime(datetime.now(UTC))
        self.user_message = Message(
            id=MessageId(uuid4()),
            chat_id=ChatId(self.chat_id),
            model_id=self.chat.settings.model_id,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
            content=self.content,
            created_at=now,
            edited_at=now,
        )

        self.chat_repository: AsyncMock = AsyncMock(
            spec=IChatRepository,
            get_by_id=AsyncMock(return_value=self.chat),
        )
        self.message_repository: AsyncMock = AsyncMock(spec=IMessageRepository)
        self.message_factory: Mock = Mock(spec=IMessageFactory)
        self.message_factory.create.return_value = self.user_message
        self.access_policy: Mock = Mock(spec=IChatAccessPolicy)

        self.command = SendMessageCommand(
            user_id=self.user_id,
            chat_id=self.chat_id,
            content=self.content,
        )

        self.use_case = SendMessageUseCase(
            chat_repository=self.chat_repository,
            message_repository=self.message_repository,
            message_factory=self.message_factory,
            access_policy=self.access_policy,
        )

    async def test_creates_user_message_and_returns_dto(self) -> None:
        result = await self.use_case.execute(self.command)

        self.message_repository.add.assert_awaited_once_with(self.user_message)

        assert isinstance(result, UUID)
        assert result == self.user_message.id.value

    async def test_calls_factory_with_correct_dto(self) -> None:
        await self.use_case.execute(self.command)

        self.message_factory.create.assert_called_once_with(
            MessageFactoryDTO(
                chat_id=ChatId(self.chat_id),
                model_id=self.chat.settings.model_id,
                role=Author.USER,
                content=self.content,
            )
        )

    async def test_calls_access_policy_with_user_and_chat(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.chat
        )

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.chat.id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)
