from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.publish_assistant_use_case import (
    PublishAssistantCommand,
)
from luminary.assistant.application.usecases.command.publish_assistant_use_case import (
    PublishAssistantUseCase,
)
from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.assistant.domain.enums import AssistantType


@pytest.mark.asyncio
class TestPublishAssistantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.assistant_id = uuid4()

        self.assistant = make_assistant(
            assistant_id=self.assistant_id,
            user_id=self.user_id,
            type=AssistantType.PERSONAL,
        )

        self.access_policy: Mock = Mock(spec=IAssistantAccessPolicy)
        self.repository: AsyncMock = AsyncMock(
            spec=IAssistantRepository,
            get_by_id=AsyncMock(return_value=self.assistant),
        )

        self.command = PublishAssistantCommand(
            user_id=self.user_id,
            assistant_id=self.assistant_id,
        )

        self.use_case = PublishAssistantUseCase(
            repository=self.repository,
            access_policy=self.access_policy,
        )

    async def test_calls_repository_get_by_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.get_by_id.assert_awaited_once_with(
            AssistantId(self.assistant_id)
        )

    async def test_calls_access_policy_with_user_and_assistant(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.assistant
        )

    async def test_changes_assistant_type_to_public(self) -> None:
        await self.use_case.execute(self.command)

        assert self.assistant.type == AssistantType.PUBLIC

    async def test_calls_repository_save(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.save.assert_awaited_once_with(self.assistant)

    async def test_raises_not_found_when_assistant_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(
            AssistantId(self.assistant_id)
        )

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.assistant.id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

    async def test_raises_invariant_error_when_publishing_non_personal(self) -> None:
        # Arrange — PUBLIC assistant (already published)
        public_assistant = make_assistant(
            assistant_id=self.assistant_id,
            user_id=self.user_id,
            type=AssistantType.PUBLIC,
        )
        self.repository.get_by_id = AsyncMock(return_value=public_assistant)

        # Act & Assert
        with pytest.raises(InvariantViolationError, match="Only personal assistants"):
            await self.use_case.execute(self.command)
