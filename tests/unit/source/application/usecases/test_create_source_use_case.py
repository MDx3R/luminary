from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from tests.unit.source.utils import (
    make_file_source,
    make_link_source,
    make_page_source,
)

from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateFileSourceCommand,
    CreateLinkSourceCommand,
    CreatePageSourceCommand,
)
from luminary.source.application.usecases.command.create_source_use_case import (
    CreateFileSourceUseCase,
    CreateLinkSourceUseCase,
    CreatePageSourceUseCase,
)
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    ISourceFactory,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)
from luminary.source.domain.value_objects.file_meta import FileMeta


@pytest.mark.asyncio
class TestCreateFileSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id: UUID = uuid4()
        self.source_id: UUID = uuid4()
        self.title = "Test File"
        self.meta = FileMeta(
            filename="test.txt",
            mime_type="text/plain",
            filesize=100,
            checksum="abc123",
        )

        self.source = make_file_source(
            source_id=self.source_id,
            owner_id=self.user_id,
            title=self.title,
            meta=self.meta,
        )

        self.source_factory: Mock = Mock(spec=ISourceFactory)
        self.source_factory.create.return_value = self.source
        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)

        self.command = CreateFileSourceCommand(
            user_id=self.user_id,
            title=self.title,
            meta=self.meta,
        )

        self.use_case = CreateFileSourceUseCase(
            source_repository=self.source_repository,
            source_factory=self.source_factory,
        )

    async def test_calls_factory_with_correct_dto(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        expected_dto = FileSourceFactoryDTO(
            owner_id=self.user_id,
            title=self.title,
            meta=self.meta,
        )
        self.source_factory.create.assert_called_once_with(expected_dto)

    async def test_calls_repository_add_with_created_source(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.source_repository.add.assert_awaited_once_with(self.source)

    async def test_returns_created_source_id(self) -> None:
        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        assert result == self.source_id


@pytest.mark.asyncio
class TestCreateLinkSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id: UUID = uuid4()
        self.source_id: UUID = uuid4()
        self.title = "Test Link"
        self.url = "https://example.com"

        self.source = make_link_source(
            source_id=self.source_id,
            owner_id=self.user_id,
            title=self.title,
            url=self.url,
        )

        self.source_factory: Mock = Mock(spec=ISourceFactory)
        self.source_factory.create.return_value = self.source
        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)

        self.command = CreateLinkSourceCommand(
            user_id=self.user_id,
            title=self.title,
            url=self.url,
        )

        self.use_case = CreateLinkSourceUseCase(
            source_repository=self.source_repository,
            source_factory=self.source_factory,
        )

    async def test_calls_factory_with_correct_dto(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        expected_dto = LinkSourceFactoryDTO(
            owner_id=self.user_id,
            title=self.title,
            url=self.url,
        )
        self.source_factory.create.assert_called_once_with(expected_dto)

    async def test_calls_repository_add_with_created_source(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.source_repository.add.assert_awaited_once_with(self.source)

    async def test_returns_created_source_id(self) -> None:
        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        assert result == self.source_id


@pytest.mark.asyncio
class TestCreatePageSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id: UUID = uuid4()
        self.source_id: UUID = uuid4()
        self.title = "Test Page"

        self.source = make_page_source(
            source_id=self.source_id,
            owner_id=self.user_id,
            title=self.title,
        )

        self.source_factory: Mock = Mock(spec=ISourceFactory)
        self.source_factory.create.return_value = self.source
        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)

        self.command = CreatePageSourceCommand(
            user_id=self.user_id,
            title=self.title,
        )

        self.use_case = CreatePageSourceUseCase(
            source_repository=self.source_repository,
            source_factory=self.source_factory,
        )

    async def test_calls_factory_with_correct_dto(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        expected_dto = PageSourceFactoryDTO(
            owner_id=self.user_id,
            title=self.title,
        )
        self.source_factory.create.assert_called_once_with(expected_dto)

    async def test_calls_repository_add_with_created_source(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.source_repository.add.assert_awaited_once_with(self.source)

    async def test_returns_created_source_id(self) -> None:
        # Act
        result = await self.use_case.execute(self.command)

        # Assert
        assert result == self.source_id
