from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.clone_assistant_use_case import (
    CloneAssistantCommand,
)
from luminary.assistant.application.usecases.command.clone_assistant_use_case import (
    CloneAssistantUseCase,
)
from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.assistant.domain.enums import AssistantType


@pytest.mark.asyncio
class TestCloneAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.assistant_id = uuid4()
        self.new_id = uuid4()

        self.assistant = make_assistant(
            assistant_id=self.assistant_id,
            user_id=self.user_id,
            tags=["python"],
        )

        self.access_policy: Mock = Mock(spec=IAssistantAccessPolicy)
        self.repository: AsyncMock = AsyncMock(
            spec=IAssistantRepository,
            get_by_id=AsyncMock(return_value=self.assistant),
        )
        self.uuid_generator = Mock()
        self.uuid_generator.create = Mock(return_value=self.new_id)

        self.command = CloneAssistantCommand(
            user_id=self.user_id,
            assistant_id=self.assistant_id,
        )

        self.use_case = CloneAssistantUseCase(
            repository=self.repository,
            access_policy=self.access_policy,
            uuid_generator=self.uuid_generator,
        )

    async def test_calls_repository_get_by_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.get_by_id.assert_awaited_once_with(
            AssistantId(self.assistant_id)
        )

    async def test_calls_assert_can_clone_with_user_and_assistant(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_can_clone.assert_called_once_with(
            UserId(self.user_id), self.assistant
        )

    async def test_returns_new_assistant_id(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.new_id

    async def test_calls_repository_add_with_clone(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.add.assert_awaited_once()
        clone = self.repository.add.call_args[0][0]
        assert clone.id.value == self.new_id
        assert clone.type == AssistantType.PERSONAL
        assert clone.owner_id == UserId(self.user_id)

    async def test_clone_preserves_tags(self) -> None:
        await self.use_case.execute(self.command)

        clone = self.repository.add.call_args[0][0]
        assert clone.tags == ["python"]

    async def test_raises_not_found_when_source_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(
            AssistantId(self.assistant_id)
        )

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_raises_access_policy_error_when_denied(self) -> None:
        self.access_policy.assert_can_clone.side_effect = AccessPolicyError(
            self.assistant.id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

    async def test_can_clone_public_assistant(self) -> None:
        # Arrange — public assistant owned by someone else
        other_user_id = uuid4()
        public_assistant = make_assistant(
            assistant_id=self.assistant_id,
            user_id=other_user_id,
            type=AssistantType.PUBLIC,
        )
        self.repository.get_by_id = AsyncMock(return_value=public_assistant)

        # Act (no exception expected from policy mock)
        result = await self.use_case.execute(self.command)

        # Assert — clone belongs to requesting user
        clone = self.repository.add.call_args[0][0]
        assert clone.owner_id == UserId(self.user_id)
        assert clone.type == AssistantType.PERSONAL
        assert isinstance(result, UUID)

    async def test_can_clone_system_assistant(self) -> None:
        # Arrange
        system_assistant = make_assistant(
            assistant_id=self.assistant_id,
            type=AssistantType.SYSTEM,
            user_id=None,
        )
        self.repository.get_by_id = AsyncMock(return_value=system_assistant)

        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        clone = self.repository.add.call_args[0][0]
        assert clone.type == AssistantType.PERSONAL
        assert clone.owner_id == UserId(self.user_id)
        assert isinstance(result, UUID)
