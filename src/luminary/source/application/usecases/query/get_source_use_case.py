"""Get source by id query use case implementation."""

from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.application.interfaces.repositories.source_read_repository import (
    ISourceReadRepository,
)
from luminary.source.application.interfaces.usecases.query.get_source_use_case import (
    GetSourceByIdQuery,
    IGetSourceByIdUseCase,
)


class GetSourceByIdUseCase(IGetSourceByIdUseCase):
    def __init__(self, read_repository: ISourceReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: GetSourceByIdQuery) -> SourceReadModel:
        return await self._read_repository.get_by_id(query.source_id, query.user_id)
