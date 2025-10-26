from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.datetime import DateTime
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.apply_assistant_to_chat import (
    ApplyAssistantToChatCommand,
)
from luminary.assistant.application.usecases.command.apply_assistant_to_chat import (
    ApplyAssistantToChatUseCase,
)
from luminary.assistant.domain.entity.assisnant import Assistant
from luminary.assistant.domain.interfaces.assistant_service import IAssistantService
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings


@pytest.mark.asyncio
class TestApplyAssistantToChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.assistant_id = uuid4()

        self.assistant = make_assistant(
            assistant_id=self.assistant_id,
            instructions=make_instructions(prompt="This is assistant prompt"),
        )

        self.chat = Chat(
            uuid4(),
            uuid4(),
            None,
            ChatInfo("Chat"),
            ChatSettings(uuid4(), "This is system prompt", 20),
            DateTime(datetime.now(UTC)),
        )

        self.assistant_service = Mock(spec=IAssistantService)
        self.assistant_access_policy = Mock(spec=IAssistantAccessPolicy)

        self.assistant_repository = AsyncMock(spec=IAssistantRepository)
        self.chat_repository = AsyncMock(spec=IChatRepository)

        self.command = ApplyAssistantToChatCommand(
            user_id=self.assistant.user_id,
            assistant_id=self.assistant.assistant_id,
            chat_id=self.chat.chat_id,
        )

        self.use_case = ApplyAssistantToChatUseCase(
            self.assistant_service,
            self.assistant_access_policy,
            self.assistant_repository,
            self.chat_repository,
        )

    def mock_service_call(self, assistant: Assistant, chat: Chat) -> None:
        assert assistant.instructions
        chat.settings = ChatSettings(
            chat.settings.model_id,
            assistant.instructions.prompt,
            chat.settings.max_context_messages,
        )

    async def test_apply_assistant_to_chat_success(self):
        # Arrange
        self.assistant_repository.get_by_id.return_value = self.assistant
        self.chat_repository.get_by_id.return_value = self.chat

        self.assistant_service.apply_assistant_instructions_to_chat.side_effect = (
            self.mock_service_call
        )

        # Act
        await self.use_case.execute(self.command)

        # Assert
        # NOTE: Changes applied on self.chat object via reference
        assert self.assistant.instructions is not None
        assert self.chat.settings.system_prompt == self.assistant.instructions.prompt

        self.assistant_repository.get_by_id.assert_awaited_once_with(
            self.command.assistant_id
        )
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.command.user_id, self.assistant
        )
        self.chat_repository.get_by_id.assert_awaited_once_with(self.command.chat_id)
        self.assistant_service.apply_assistant_instructions_to_chat.assert_called_once_with(
            self.assistant, self.chat
        )
        self.chat_repository.save.assert_awaited_once_with(self.chat)

    async def test_assistant_access_denied_raises(self):
        # Arrange
        self.assistant_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.assistant.assistant_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.assistant_repository.get_by_id.assert_awaited_once_with(
            self.assistant.assistant_id
        )
        self.chat_repository.save.assert_not_awaited()

    @pytest.mark.skip
    async def test_chat_access_denied_raises(self):
        # TODO: Add
        ...
