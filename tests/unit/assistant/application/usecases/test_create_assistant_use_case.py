from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
)
from luminary.assistant.application.usecases.command.create_assistant_use_case import (
    CreateAssistantUseCase,
)


@pytest.mark.asyncio
class TestCreateAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.assistant_id = uuid4()

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.assistant_id

        self.assistant_repository = AsyncMock(spec=IAssistantRepository)

        self.assistant = make_assistant(assistant_id=self.assistant_id)

        self.command = CreateAssistantCommand(
            user_id=self.assistant.user_id,
            name=self.assistant.name,
            description=self.assistant.description,
            prompt=None,
        )

        self.use_case = CreateAssistantUseCase(
            self.uuid_generator, self.assistant_repository
        )

    async def test_create_assistant_success(self):
        # Arrange
        self.assistant_repository.exists_by_name_for_user.return_value = False

        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        assert result == self.assistant_id
        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            self.command.name, self.command.user_id
        )
        self.assistant_repository.add.assert_awaited_once_with(self.assistant)

    async def test_create_assistant_with_instructions(self):
        # Arrange
        prompt = "Prompt"
        assistant = make_assistant(
            assistant_id=self.assistant_id,
            instructions=make_instructions(prompt=prompt),
        )

        command = CreateAssistantCommand(
            user_id=assistant.user_id,
            name=assistant.name,
            description=assistant.description,
            prompt=prompt,
        )

        self.assistant_repository.exists_by_name_for_user.return_value = False

        # Act
        result = await self.use_case.execute(command)

        # Assert
        assert result == self.assistant_id
        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            command.name, command.user_id
        )
        self.assistant_repository.add.assert_awaited_once_with(assistant)

    async def test_create_assistant_duplicate_name(self):
        # Arrange
        self.assistant_repository.exists_by_name_for_user.return_value = True

        # Act & Assert
        with pytest.raises(AssistantDuplicateNameError):
            await self.use_case.execute(self.command)

        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            self.command.name, self.command.user_id
        )
        self.assistant_repository.add.assert_not_awaited()

    async def test_create_assistant_invalid_name(self):
        # Arrange
        command = CreateAssistantCommand(
            user_id=uuid4(),
            name="",
            description="Test Description",
            prompt="Test Prompt",
        )
        self.assistant_repository.exists_by_name_for_user.return_value = False

        # Act & Assert
        with pytest.raises(InvariantViolationError):
            await self.use_case.execute(command)

        self.assistant_repository.add.assert_not_awaited()
