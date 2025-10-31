from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.datetime import DateTime

from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateSourceCommand,
)
from luminary.source.application.usecases.command.create_source_use_case import (
    CreateSourceUseCase,
)
from luminary.source.domain.entity.source import Source
from luminary.source.domain.interfaces.source_factory import ISourceFactory


def make_source(
    source_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Source",
    created_at: DateTime | None = None,
) -> Source:
    return Source(
        source_id=source_id or uuid4(),
        user_id=user_id or uuid4(),
        name=name,
        created_at=created_at or DateTime(datetime.now(UTC)),
    )


@pytest.mark.asyncio
class TestCreateSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id: UUID = uuid4()
        self.source_id: UUID = uuid4()

        self.source: Source = make_source(
            source_id=self.source_id, user_id=self.user_id
        )
        self.source_factory: Mock = Mock(spec=ISourceFactory)
        self.source_factory.create.return_value = self.source

        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)

        self.command: CreateSourceCommand = CreateSourceCommand(
            user_id=self.user_id, name="Test Source"
        )

        self.use_case: CreateSourceUseCase = CreateSourceUseCase(
            repository=self.source_repository,
            factory=self.source_factory,
        )

    async def test_calls_factory_with_user_id(self) -> None:
        await self.use_case.execute(self.command)

        _, call_kwargs = self.source_factory.create.call_args
        assert call_kwargs["user_id"] == self.user_id

    async def test_calls_factory_with_name(self) -> None:
        await self.use_case.execute(self.command)

        _, call_kwargs = self.source_factory.create.call_args
        assert call_kwargs["name"] == "Test Source"

    async def test_calls_repository_add_with_created_source(self) -> None:
        await self.use_case.execute(self.command)

        self.source_repository.add.assert_awaited_once_with(self.source)

    async def test_returns_created_source_id(self) -> None:
        result: UUID = await self.use_case.execute(self.command)

        assert result == self.source_id
