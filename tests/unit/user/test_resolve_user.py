from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.user.application.dtos.profile import ExternalProfile, UserProfile
from luminary.user.application.interfaces.user_repository import IUserRepository
from luminary.user.application.usecases.resolve_user_use_case import ResolveUserUseCase


@pytest.mark.asyncio
async def test_resolve_uses_local_id_and_verified_profile():
    repository = AsyncMock(spec=IUserRepository)
    generator = Mock(spec=IUUIDGenerator)
    local_id, candidate_id = uuid4(), uuid4()
    profile = ExternalProfile("zitadel-sub", "Jane Doe", "jane@example.com")
    generator.create.return_value = candidate_id
    repository.upsert.return_value = UserProfile(local_id, profile.name, profile.email)
    use_case = ResolveUserUseCase(repository, generator)

    result = await use_case.execute(profile, "jane")

    assert result.identity_id == local_id
    assert result.username == "jane"
    assert result.name == profile.name
    assert result.email == profile.email
    repository.upsert.assert_awaited_once_with(candidate_id, profile)


@pytest.mark.asyncio
async def test_repository_errors_are_not_reported_as_authentication_errors():
    repository = AsyncMock(spec=IUserRepository)
    repository.upsert.side_effect = RuntimeError("database unavailable")
    profile = ExternalProfile("sub", "Jane", "jane@test.io")
    use_case = ResolveUserUseCase(repository, Mock(spec=IUUIDGenerator))

    with pytest.raises(RuntimeError, match="database unavailable"):
        await use_case.execute(profile, "jane")
