from luminary.source.application.dto.source_dto import SourceDTO, UpdateSourceDTO
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    IUpdateSourceUseCase,
)
from luminary.source.domain.entity.source import Source


class UpdateSourceUseCase(IUpdateSourceUseCase):
    def __init__(self, repository: ISourceRepository) -> None:
        self.repository = repository

    async def execute(self, dto: UpdateSourceDTO) -> SourceDTO:
        source = await self.repository.get_by_id(dto.source_id)
        updated_source = Source.create(
            source_id=source.source_id,
            user_id=source.user_id,
            name=dto.name,
            created_at=source.created_at,
        )
        await self.repository.save(updated_source)
        return SourceDTO(
            source_id=updated_source.source_id,
            user_id=updated_source.user_id,
            name=updated_source.name,
            created_at=updated_source.created_at.value,
        )
