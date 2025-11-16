from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant, make_instructions
from tests.unit.chat.utils import make_chat

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.entity.assisnant import Assistant, AssistantId
from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.apply_assistant_to_chat import (
    ApplyAssistantToChatCommand,
)
from luminary.chat.application.usecases.command.apply_assistant_to_chat import (
    ApplyAssistantToChatUseCase,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_settings import ChatSettings


@pytest.mark.asyncio
class TestApplyAssistantToChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.assistant_id = AssistantId(uuid4())
        self.chat_id = ChatId(uuid4())

        self.assistant = make_assistant(
            assistant_id=self.assistant_id.value,
            user_id=self.user_id.value,
            instructions=make_instructions(prompt="This is assistant prompt"),
        )

        self.chat = make_chat(chat_id=self.chat_id.value)

        self.assistant_access_policy = Mock(spec=IAssistantAccessPolicy)

        self.chat_access_policy = Mock(spec=IChatAccessPolicy)

        self.assistant_repository = AsyncMock(spec=IAssistantRepository)
        self.chat_repository = AsyncMock(spec=IChatRepository)

        self.command = ApplyAssistantToChatCommand(
            user_id=self.user_id.value,
            assistant_id=self.assistant_id.value,
            chat_id=self.chat_id.value,
        )

        self.use_case = ApplyAssistantToChatUseCase(
            self.assistant_access_policy,
            self.assistant_repository,
            self.chat_repository,
            self.chat_access_policy,
        )

    def mock_service_call(self, assistant: Assistant, chat: Chat) -> None:
        chat.settings = ChatSettings(
            chat.settings.model_id, chat.settings.max_context_messages
        )

    async def test_apply_assistant_to_chat_success(self):
        # Arrange
        self.assistant_repository.get_by_id.return_value = self.assistant
        self.chat_repository.get_by_id.return_value = self.chat

        # Act
        await self.use_case.execute(self.command)

        # Assert
        # NOTE: Changes applied on self.chat object via reference
        assert self.chat.assistant_id == self.assistant.id

        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.assistant
        )
        self.chat_repository.get_by_id.assert_awaited_once_with(self.chat_id)
        self.chat_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.chat
        )
        self.chat_repository.save.assert_awaited_once_with(self.chat)

    async def test_assistant_access_denied_raises(self):
        # Arrange
        self.chat_repository.get_by_id.return_value = self.chat
        self.assistant_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.assistant.id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.chat_repository.save.assert_not_awaited()

    async def test_chat_access_denied_raises(self):
        # Arrange
        self.chat_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.chat.id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.chat_repository.get_by_id.assert_awaited_once_with(self.chat_id)
        self.chat_repository.save.assert_not_awaited()
