from luminary.source.application.dto.source_dto import DeleteSourceDTO
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.delete_source_use_case import (
    IDeleteSourceUseCase,
)


class DeleteSourceUseCase(IDeleteSourceUseCase):
    def __init__(self, repository: ISourceRepository) -> None:
        self.repository = repository

    async def execute(self, dto: DeleteSourceDTO) -> None:
        await self.repository.delete(dto.source_id)
