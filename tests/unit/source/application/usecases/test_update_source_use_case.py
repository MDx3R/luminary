from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.source.utils import make_source

from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    UpdateSourceCommand,
)
from luminary.source.application.usecases.command.update_source_use_case import (
    UpdateSourceUseCase,
)
from luminary.source.domain.entity.source import Source, SourceId


@pytest.mark.asyncio
class TestUpdateSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = UserId(uuid4())
        self.source_id = SourceId(uuid4())

        self.source: Source = make_source(
            source_id=self.source_id.value,
            owner_id=self.user_id.value,
            title="Old Name",
        )

        self.access_policy: Mock = Mock(spec=ISourceAccessPolicy)
        self.repository: AsyncMock = AsyncMock(
            spec=ISourceRepository, get_by_id=AsyncMock(return_value=self.source)
        )

        self.command = UpdateSourceCommand(
            user_id=self.user_id.value,
            source_id=self.source_id.value,
            title="New Name",
        )

        self.use_case: UpdateSourceUseCase = UpdateSourceUseCase(
            repository=self.repository,
            access_policy=self.access_policy,
        )

    async def test_calls_repository_get_by_id_with_source_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.get_by_id.assert_awaited_once_with(self.source_id)

    async def test_calls_access_policy_with_user_and_source(self) -> None:
        await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, self.source
        )

    async def test_updates_source_name(self) -> None:
        await self.use_case.execute(self.command)

        assert self.source.title.value == "New Name"

    async def test_calls_repository_save_with_updated_source(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.save.assert_awaited_once_with(self.source)

    async def test_skips_save_when_name_unchanged(self) -> None:
        unchanged_command = UpdateSourceCommand(
            user_id=self.user_id.value,
            source_id=self.source_id.value,
            title="Old Name",
        )

        await self.use_case.execute(unchanged_command)

        self.repository.save.assert_not_awaited()

    async def test_raises_not_found_error_when_source_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_does_not_check_access_when_source_not_found(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_not_called()

    async def test_does_not_save_when_source_not_found(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        self.repository.save.assert_not_awaited()

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.source_id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

    async def test_does_not_save_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.source_id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.repository.save.assert_not_awaited()

    async def test_raises_invariant_violation_when_name_is_empty(self) -> None:
        invalid_command = UpdateSourceCommand(
            user_id=self.user_id.value,
            source_id=self.source_id.value,
            title="",
        )

        with pytest.raises(InvariantViolationError):
            await self.use_case.execute(invalid_command)

    async def test_raises_invariant_violation_when_name_is_whitespace(self) -> None:
        invalid_command = UpdateSourceCommand(
            user_id=self.user_id.value,
            source_id=self.source_id.value,
            title="   ",
        )

        with pytest.raises(InvariantViolationError):
            await self.use_case.execute(invalid_command)
