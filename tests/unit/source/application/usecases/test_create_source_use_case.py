from io import BytesIO
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import FileId
from tests.unit.source.utils import (
    make_file_source,
    make_link_source,
    make_page_source,
)

from luminary.content.application.interfaces.services.content_service import (
    IContentService,
    ProcessFileCommand,
)
from luminary.content.domain.entity.content import ContentId
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


@pytest.mark.asyncio
class TestCreateFileSourceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.source_id = uuid4()
        self.title = "Test File"
        self.file_id = uuid4()

        self.source = make_file_source(
            source_id=self.source_id,
            owner_id=self.user_id,
            title=self.title,
        )

        self.source_factory: Mock = Mock(
            spec=ISourceFactory, create=Mock(return_value=self.source)
        )
        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)

        self.command = CreateFileSourceCommand(
            user_id=self.user_id, title=self.title, file_id=self.file_id
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
            owner_id=UserId(self.user_id),
            title=self.title,
            file_id=FileId(self.file_id),
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

        self.source_factory: Mock = Mock(
            spec=ISourceFactory, create=Mock(return_value=self.source)
        )
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
            owner_id=UserId(self.user_id),
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
        self.content_id: UUID = uuid4()
        self.title = "Test Page"

        self.source = make_page_source(
            source_id=self.source_id,
            owner_id=self.user_id,
            title=self.title,
        )

        self.source_factory: Mock = Mock(
            spec=ISourceFactory, create=Mock(return_value=self.source)
        )
        self.source_repository: AsyncMock = AsyncMock(spec=ISourceRepository)
        self.content_service = AsyncMock(
            spec=IContentService, process_file=AsyncMock(return_value=self.content_id)
        )

        self.command = CreatePageSourceCommand(
            user_id=self.user_id, title=self.title, data=BytesIO(b"content")
        )

        self.use_case = CreatePageSourceUseCase(
            source_repository=self.source_repository,
            source_factory=self.source_factory,
            content_service=self.content_service,
        )

    async def test_calls_factory_with_correct_dto(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        expected_dto = PageSourceFactoryDTO(
            owner_id=UserId(self.user_id),
            title=self.title,
            content_id=ContentId(self.content_id),
        )
        self.source_factory.create.assert_called_once_with(expected_dto)

    async def test_calls_content_service_with_recieved_data(self) -> None:
        # Act
        await self.use_case.execute(self.command)

        # Assert
        self.content_service.process_file.assert_awaited_once_with(
            ProcessFileCommand(
                user_id=self.user_id, data=self.command.data, filename=self.title
            )
        )

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
