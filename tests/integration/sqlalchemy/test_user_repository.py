import asyncio
from uuid import uuid4

import pytest
from cli.users.link import link_user
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import (
    MakerSessionFactory,
)
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy import func, select

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.infrastructure.database.postgres.sqlalchemy.models.user_base import (
    UserBase,
)
from luminary.user.infrastructure.database.postgres.sqlalchemy.repositories.user_repository import (
    UserRepository,
)


@pytest.fixture
def repository(maker):
    return UserRepository(QueryExecutor(UnitOfWork(MakerSessionFactory(maker))))


@pytest.mark.asyncio
async def test_upsert_preserves_local_id_and_updates_profile(repository, maker):
    user_id = uuid4()
    first = await repository.upsert(
        user_id, ExternalProfile("sub", "Jane", "old@test.io")
    )
    updated = await repository.upsert(
        uuid4(), ExternalProfile("sub", "Jane Doe", "new@test.io")
    )
    assert first.id == updated.id == user_id
    assert updated.name == "Jane Doe"
    assert updated.email == "new@test.io"
    async with maker() as session:
        assert await session.scalar(select(func.count()).select_from(UserBase)) == 1


@pytest.mark.asyncio
async def test_concurrent_first_requests_create_one_user(repository, maker):
    profile = ExternalProfile("sub", "Jane", "jane@test.io")
    results = await asyncio.gather(
        *(repository.upsert(uuid4(), profile) for _ in range(8))
    )
    assert len({user.id for user in results}) == 1
    async with maker() as session:
        assert await session.scalar(select(func.count()).select_from(UserBase)) == 1


@pytest.mark.asyncio
async def test_equal_names_and_emails_do_not_merge_users(repository):
    first = await repository.upsert(
        uuid4(), ExternalProfile("one", "Jane", "same@test.io")
    )
    second = await repository.upsert(
        uuid4(), ExternalProfile("two", "Jane", "same@test.io")
    )
    assert first.id != second.id


@pytest.mark.asyncio
async def test_explicit_legacy_link_preserves_owner_id(repository, maker):
    user_id = uuid4()
    async with maker() as session:
        session.add(UserBase(user_id=user_id, name="legacy"))
        await session.commit()
        await link_user(session, user_id, "new-sub")
    result = await repository.upsert(
        uuid4(), ExternalProfile("new-sub", "Jane", "jane@test.io")
    )
    assert result.id == user_id


@pytest.mark.asyncio
async def test_link_cannot_reassign_existing_subject(repository, maker):
    existing = await repository.upsert(
        uuid4(), ExternalProfile("sub", "Jane", "jane@test.io")
    )
    legacy_id = uuid4()
    async with maker() as session:
        session.add(UserBase(user_id=legacy_id, name="legacy"))
        await session.commit()
        with pytest.raises(ValueError, match="already linked to another user"):
            await link_user(session, legacy_id, "sub")
        with pytest.raises(ValueError, match="already linked"):
            await link_user(session, existing.id, "different-sub")


@pytest.mark.asyncio
async def test_link_rejects_missing_user(maker):
    async with maker() as session:
        with pytest.raises(ValueError, match="does not exist"):
            await link_user(session, uuid4(), "sub")
