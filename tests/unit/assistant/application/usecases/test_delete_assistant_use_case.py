from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    DeleteAssistantCommand,
)
from luminary.assistant.application.usecases.command.delete_assistant_use_case import (
    DeleteAssistantUseCase,
)
from luminary.assistant.domain.entity.assisnant import AssistantId


@pytest.mark.asyncio
class TestCreateAssistantUseCase:
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

        self.command = DeleteAssistantCommand(
            user_id=self.user_id.value,
            assistant_id=self.assistant_id.value,
        )

        self.use_case = DeleteAssistantUseCase(
            self.assistant_access_policy, self.assistant_repository
        )

    async def test_delete_assistant_success(self):
        # Act
        await self.use_case.execute(self.command)  # no error

        # Assert
        assert self.assistant.is_deleted is True
        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.assistant
        )
        self.assistant_repository.save.assert_awaited_once_with(self.assistant)

    async def test_delete_assistant_not_found_raises(self):
        # Arrange
        self.assistant_repository.get_by_id.side_effect = NotFoundError(
            self.assistant_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        assert self.assistant.is_deleted is False
        self.assistant_repository.get_by_id.assert_awaited_once_with(self.assistant_id)
        self.assistant_access_policy.assert_is_allowed.assert_not_called()
        self.assistant_repository.save.assert_not_awaited()
