from uuid import UUID

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
        # TODO: Remove meta, consider different flow
        source = self.source_factory.create(
            FileSourceFactoryDTO(
                owner_id=command.user_id, title=command.title, meta=command.meta
            )
        )
        await self.source_repository.add(source)
        return source.source_id


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
                owner_id=command.user_id, title=command.title, url=command.url
            )
        )
        await self.source_repository.add(source)
        return source.source_id


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
            PageSourceFactoryDTO(owner_id=command.user_id, title=command.title)
        )
        await self.source_repository.add(source)
        return source.source_id
