from uuid import UUID

from common.domain.value_objects.id import UserId

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
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory

    async def execute(self, command: CreateFileSourceCommand) -> UUID:
        # TODO: Consider different flow
        source = self.source_factory.create(
            FileSourceFactoryDTO(
                owner_id=UserId(command.user_id),
                title=command.title,
                file_id=command.file_id,
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
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory

    async def execute(self, command: CreatePageSourceCommand) -> UUID:
        source = self.source_factory.create(
            PageSourceFactoryDTO(
                owner_id=UserId(command.user_id),
                title=command.title,
                content_id=command.content_id,
            )
        )
        await self.source_repository.add(source)
        return source.id.value
