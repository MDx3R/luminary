"""List assistants query use case implementation."""

from collections.abc import Sequence

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.list_assistants_use_case import (
    IListAssistantsUseCase,
    ListAssistantsQuery,
)


class ListAssistantsUseCase(IListAssistantsUseCase):
    def __init__(self, read_repository: IAssistantReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(
        self, query: ListAssistantsQuery
    ) -> Sequence[AssistantSummaryReadModel]:
        return await self._read_repository.list_by_owner(query.user_id)
