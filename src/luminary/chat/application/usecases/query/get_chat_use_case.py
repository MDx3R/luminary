"""Get chat by id query use case implementation."""

from luminary.chat.application.dtos.read_models import ChatReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatByIdQuery,
    IGetChatByIdUseCase,
)


class GetChatByIdUseCase(IGetChatByIdUseCase):
    def __init__(self, read_repository: IChatReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: GetChatByIdQuery) -> ChatReadModel:
        return await self._read_repository.get_by_id(query.chat_id, query.user_id)
