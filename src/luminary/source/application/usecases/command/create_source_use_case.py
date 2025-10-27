from luminary.source.application.dto.source_dto import CreateSourceDTO, SourceDTO
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
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

    async def execute(self, dto: CreateSourceDTO) -> SourceDTO:
        source = self.factory.create(user_id=dto.user_id, name=dto.name)
        await self.repository.add(source)
        return SourceDTO(
            source_id=source.source_id,
            user_id=source.user_id,
            name=source.name,
            created_at=source.created_at.value,
        )
