"""Get assistant by id query use case implementation."""

from luminary.assistant.application.dtos.read_models import AssistantReadModel
from luminary.assistant.application.interfaces.repositories.assistant_read_repository import (
    IAssistantReadRepository,
)
from luminary.assistant.application.interfaces.usecases.query.get_assistant_use_case import (
    GetAssistantByIdQuery,
    IGetAssistantByIdUseCase,
)


class GetAssistantByIdUseCase(IGetAssistantByIdUseCase):
    def __init__(self, read_repository: IAssistantReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: GetAssistantByIdQuery) -> AssistantReadModel:
        return await self._read_repository.get_by_id(query.assistant_id, query.user_id)
