from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.user.application.dtos.profile import ExternalProfile, UserProfile
from luminary.user.application.exceptions import InvalidIdentityError
from luminary.user.application.interfaces.profile_provider import IProfileProvider
from luminary.user.application.interfaces.user_repository import IUserRepository
from luminary.user.application.usecases.resolve_user_use_case import ResolveUserUseCase


@pytest.mark.asyncio
async def test_resolve_uses_local_id_and_verified_profile():
    provider = AsyncMock(spec=IProfileProvider)
    repository = AsyncMock(spec=IUserRepository)
    generator = Mock(spec=IUUIDGenerator)
    local_id, candidate_id = uuid4(), uuid4()
    profile = ExternalProfile("zitadel-sub", "Jane Doe", "jane@example.com")
    generator.create.return_value = candidate_id
    provider.get_profile.return_value = profile
    repository.upsert.return_value = UserProfile(local_id, profile.name, profile.email)
    use_case = ResolveUserUseCase(provider, repository, generator)

    result = await use_case.execute("zitadel-sub", "jane", "access-token")

    assert result.identity_id == local_id
    assert result.username == "jane"
    assert result.name == profile.name
    assert result.email == profile.email
    provider.get_profile.assert_awaited_once_with("access-token")
    repository.upsert.assert_awaited_once_with(candidate_id, profile)


@pytest.mark.asyncio
async def test_subject_mismatch_cannot_create_or_access_another_user():
    provider = AsyncMock(spec=IProfileProvider)
    repository = AsyncMock(spec=IUserRepository)
    provider.get_profile.return_value = ExternalProfile(
        "actual", "Jane", "jane@test.io"
    )
    use_case = ResolveUserUseCase(provider, repository, Mock(spec=IUUIDGenerator))

    with pytest.raises(InvalidIdentityError):
        await use_case.execute("victim", "jane", "valid-token-for-actual")

    repository.upsert.assert_not_awaited()
