from uuid import UUID

from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateSourceCommand,
    ICreateSourceUseCase,
)
from luminary.source.domain.interfaces.source_factory import ISourceFactory


class CreateSourceUseCase(ICreateSourceUseCase):
    def __init__(
        self,
        repository: ISourceRepository,
        factory: ISourceFactory,
    ) -> None:
        self.repository = repository
        self.factory = factory

    async def execute(self, command: CreateSourceCommand) -> UUID:
        source = self.factory.create(user_id=command.user_id, name=command.name)
        await self.repository.add(source)
        return source.source_id
