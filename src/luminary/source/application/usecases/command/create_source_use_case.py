from uuid import UUID

from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import FileId

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
    ICreateFileSourceUseCase,
    ICreateLinkSourceUseCase,
    ICreatePageSourceUseCase,
)
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    ISourceFactory,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)


class CreateFileSourceUseCase(ICreateFileSourceUseCase):
    def __init__(
        self,
        source_factory: ISourceFactory,
        source_repository: ISourceRepository,
    ) -> None:
        self.source_factory = source_factory
        self.source_repository = source_repository

    async def execute(self, command: CreateFileSourceCommand) -> UUID:
        source = self.source_factory.create(
            FileSourceFactoryDTO(
                owner_id=UserId(command.user_id),
                title=command.title,
                file_id=FileId(command.file_id),
            )
        )
        await self.source_repository.add(source)
        return source.id.value


class CreateLinkSourceUseCase(ICreateLinkSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory

    async def execute(self, command: CreateLinkSourceCommand) -> UUID:
        source = self.source_factory.create(
            LinkSourceFactoryDTO(
                owner_id=UserId(command.user_id), title=command.title, url=command.url
            )
        )
        await self.source_repository.add(source)
        return source.id.value


class CreatePageSourceUseCase(ICreatePageSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
        content_service: IContentService,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory
        self.content_service = content_service

    async def execute(self, command: CreatePageSourceCommand) -> UUID:
        user_id = command.user_id
        content_id = await self.content_service.process_file(
            ProcessFileCommand(
                user_id=user_id, data=command.data, filename=command.title
            )
        )
        source = self.source_factory.create(
            PageSourceFactoryDTO(
                owner_id=UserId(user_id),
                title=command.title,
                content_id=ContentId(content_id),
            )
        )
        await self.source_repository.add(source)
        return source.id.value
