from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateSourceCommand,
    ICreateSourceUseCase,
    SourceDTO,
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

    async def execute(self, command: CreateSourceCommand) -> SourceDTO:
        source = self.factory.create(user_id=command.user_id, name=command.name)
        await self.repository.add(source)
        return SourceDTO(
            source_id=source.source_id,
            user_id=source.user_id,
            name=source.name,
            created_at=source.created_at,
        )
