from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
)
from luminary.assistant.application.usecases.command.create_assistant_use_case import (
    CreateAssistantUseCase,
)
from luminary.assistant.domain.enums import AssistantType
from luminary.assistant.domain.interfaces.assistant_factory import IAssistantFactory


@pytest.mark.asyncio
class TestCreateAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.assistant_id = uuid4()
        self.name = "Test Assistant"
        self.description = "Test Description"
        self.prompt = "You are helpful"

        self.assistant = make_assistant(
            assistant_id=self.assistant_id,
            user_id=self.user_id,
            name=self.name,
            description=self.description,
        )

        self.assistant_factory: Mock = Mock(
            spec=IAssistantFactory, create=Mock(return_value=self.assistant)
        )
        self.assistant_repository: AsyncMock = AsyncMock(
            spec=IAssistantRepository
        )

        self.command = CreateAssistantCommand(
            user_id=self.user_id,
            name=self.name,
            description=self.description,
            prompt=self.prompt,
        )

        self.use_case = CreateAssistantUseCase(
            assistant_factory=self.assistant_factory,
            assistant_repository=self.assistant_repository,
        )

    async def test_calls_factory_with_correct_params(self) -> None:
        await self.use_case.execute(self.command)

        self.assistant_factory.create.assert_called_once_with(
            user_id=UserId(self.user_id),
            name=self.name,
            description=self.description,
            prompt=self.prompt,
            type=AssistantType.PERSONAL,
        )

    async def test_calls_repository_add_with_created_assistant(self) -> None:
        await self.use_case.execute(self.command)

        self.assistant_repository.add.assert_awaited_once_with(self.assistant)

    async def test_returns_created_assistant_id(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.assistant_id
