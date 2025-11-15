from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.id import UserId
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
from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.assistant.domain.interfaces.assistant_factory import IAssistantFactory


@pytest.mark.asyncio
class TestCreateAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.assistant_id = AssistantId(uuid4())

        self.assistant = make_assistant(
            assistant_id=self.assistant_id.value, user_id=self.user_id.value
        )

        self.assistant_repository = AsyncMock(spec=IAssistantRepository)

        self.assistant_factory = Mock(spec=IAssistantFactory)
        self.assistant_factory.create.return_value = self.assistant

        self.command = CreateAssistantCommand(
            user_id=self.user_id.value,
            name=self.assistant.info.name,
            description=self.assistant.info.description,
            prompt=None,
        )

        self.use_case = CreateAssistantUseCase(
            self.assistant_factory, self.assistant_repository
        )

    async def test_create_assistant_success(self):
        # Arrange
        self.assistant_repository.exists_by_name_for_user.return_value = False

        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        assert result == self.assistant_id.value
        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            self.command.name, self.user_id
        )
        self.assistant_repository.add.assert_awaited_once_with(self.assistant)

    async def test_create_assistant_with_instructions(self):
        # Arrange
        prompt = "Prompt"
        assistant = make_assistant(
            assistant_id=self.assistant_id.value,
            user_id=self.user_id.value,
            instructions=make_instructions(prompt=prompt),
        )
        self.assistant_factory.create.return_value = assistant

        command = CreateAssistantCommand(
            user_id=assistant.owner_id.value,
            name=assistant.info.name,
            description=assistant.info.description,
            prompt=prompt,
        )

        self.assistant_repository.exists_by_name_for_user.return_value = False

        # Act
        result = await self.use_case.execute(command)

        # Assert
        assert result == self.assistant_id.value
        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            command.name, self.user_id
        )
        self.assistant_repository.add.assert_awaited_once_with(assistant)

    async def test_create_assistant_duplicate_name(self):
        # Arrange
        self.assistant_repository.exists_by_name_for_user.return_value = True

        # Act & Assert
        with pytest.raises(AssistantDuplicateNameError):
            await self.use_case.execute(self.command)

        self.assistant_repository.exists_by_name_for_user.assert_awaited_once_with(
            self.command.name, self.user_id
        )
        self.assistant_repository.add.assert_not_awaited()
