from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_use_case import (
    UpdateAssistantCommand,
)
from luminary.assistant.application.usecases.command.update_assistant_use_case import (
    UpdateAssistantUseCase,
)
from luminary.assistant.domain.entity.assisnant import AssistantId


@pytest.mark.asyncio
class TestUpdateAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.assistant_id = AssistantId(uuid4())

        self.assistant = make_assistant(
            assistant_id=self.assistant_id.value, user_id=self.user_id.value
        )

        self.assistant_access_policy = Mock(spec=IAssistantAccessPolicy)
        self.assistant_repository = AsyncMock(spec=IAssistantRepository)

        self.assistant_repository.get_by_id.return_value = self.assistant

        self.command = UpdateAssistantCommand(
            user_id=self.assistant.owner_id.value,
            assistant_id=self.assistant.id.value,
            name="New Name",
            description="New Description",
            prompt=None,
        )

        self.use_case = UpdateAssistantUseCase(
            self.assistant_access_policy, self.assistant_repository
        )

    async def test_update_assistant_success_no_prompt(self):
        # Act
        await self.use_case.execute(self.command)

        # Assert
        # NOTE: Changes applied on self.assistant object via reference
        assert self.assistant.info.name == self.command.name
        assert self.assistant.info.description == self.command.description
        assert self.assistant.instructions is not None  # TODO: Check default prompt

        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.assistant
        )
        self.assistant_repository.save.assert_awaited_once_with(self.assistant)

    async def test_update_assistant_change_instructions(self):
        # Arrange
        prompt = "New prompt"
        command = UpdateAssistantCommand(
            user_id=self.user_id.value,
            assistant_id=self.assistant_id.value,
            name=self.assistant.info.name,
            description=self.assistant.info.description,
            prompt=prompt,
        )

        # Act
        await self.use_case.execute(command)
        # NOTE: Changes applied on self.assistant object via reference
        assert self.assistant.info.name == command.name
        assert self.assistant.info.description == command.description
        assert self.assistant.instructions.prompt == command.prompt

        # Assert
        self.assistant_repository.get_by_id.assert_awaited()
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.assistant
        )
        self.assistant_repository.save.assert_awaited_once_with(self.assistant)

    async def test_update_assistant_reset_instructions(self):
        # Arrange
        assistant = make_assistant(
            assistant_id=self.assistant_id.value,
            user_id=self.user_id.value,
            instructions=make_instructions(prompt="p"),  # NOTE: Add instructions
        )
        self.assistant_repository.get_by_id.return_value = assistant

        command = UpdateAssistantCommand(
            user_id=self.assistant.owner_id.value,
            assistant_id=self.assistant.id.value,
            name=assistant.info.name,
            description=assistant.info.description,
            prompt=None,
        )

        # Act
        await self.use_case.execute(command)
        assert self.assistant.info.name == command.name
        assert self.assistant.info.description == command.description
        assert self.assistant.instructions is not None  # TODO: Check default prompt

        # Assert
        self.assistant_repository.get_by_id.assert_awaited()
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, assistant
        )
        # NOTE: Changes applied on assistant object via reference
        self.assistant_repository.save.assert_awaited_once_with(assistant)

    async def test_update_assistant_not_found_raises(self):
        # Arrange
        self.assistant_repository.get_by_id.side_effect = NotFoundError(
            self.assistant_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_access_policy.assert_is_allowed.assert_not_called()
        self.assistant_repository.save.assert_not_awaited()

    async def test_update_assistant_access_denied_raises(self):
        # Arrange
        self.assistant_access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.assistant_id, "denied"
        )

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_repository.save.assert_not_awaited()
