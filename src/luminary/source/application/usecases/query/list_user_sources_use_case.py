"""List user sources query use case implementation."""

from collections.abc import Sequence

from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.application.interfaces.repositories.source_read_repository import (
    ISourceReadRepository,
)
from luminary.source.application.interfaces.usecases.query.list_user_sources_use_case import (
    IListUserSourcesUseCase,
    ListUserSourcesQuery,
)


class ListUserSourcesUseCase(IListUserSourcesUseCase):
    def __init__(self, read_repository: ISourceReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: ListUserSourcesQuery) -> Sequence[SourceReadModel]:
        return await self._read_repository.list_by_owner(query.user_id)
