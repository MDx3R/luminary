from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.application.exceptions import AccessPolicyError, NotFoundError
from tests.unit.source.utils import make_source

from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.delete_source_use_case import (
    DeleteSourceCommand,
)
from luminary.source.application.usecases.command.delete_source_use_case import (
    DeleteSourceUseCase,
)
from luminary.source.domain.entity.source import Source


@pytest.mark.asyncio
class TestDeleteSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id: UUID = uuid4()
        self.source_id: UUID = uuid4()

        self.source: Source = make_source(
            source_id=self.source_id, owner_id=self.user_id
        )

        self.access_policy: Mock = Mock(spec=ISourceAccessPolicy)
        self.repository: AsyncMock = AsyncMock(spec=ISourceRepository)
        self.repository.get_by_id.return_value = self.source

        self.command: DeleteSourceCommand = DeleteSourceCommand(
            user_id=self.user_id,
            source_id=self.source_id,
        )

        self.use_case: DeleteSourceUseCase = DeleteSourceUseCase(
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

    async def test_calls_repository_delete_with_source_id(self) -> None:
        await self.use_case.execute(self.command)

        self.repository.remove.assert_awaited_once_with(self.source)

    async def test_raises_not_found_error_when_source_not_exists(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

    async def test_does_not_check_access_when_source_not_found(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        self.access_policy.assert_is_allowed.assert_not_called()

    async def test_does_not_delete_when_source_not_found(self) -> None:
        self.repository.get_by_id.side_effect = NotFoundError(self.source_id)

        with pytest.raises(NotFoundError):
            await self.use_case.execute(self.command)

        self.repository.remove.assert_not_awaited()

    async def test_raises_access_policy_error_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.source_id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

    async def test_does_not_delete_when_access_denied(self) -> None:
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.source_id, "Access denied"
        )

        with pytest.raises(AccessPolicyError):
            await self.use_case.execute(self.command)

        self.repository.remove.assert_not_awaited()
