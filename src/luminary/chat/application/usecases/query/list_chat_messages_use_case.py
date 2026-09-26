"""List chat messages query use case implementation."""

from collections.abc import Sequence

from luminary.chat.application.dtos.read_models import MessageReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.list_chat_messages_use_case import (
    IListChatMessagesUseCase,
    ListChatMessagesQuery,
)


class ListChatMessagesUseCase(IListChatMessagesUseCase):
    def __init__(self, read_repository: IChatReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: ListChatMessagesQuery) -> Sequence[MessageReadModel]:
        return await self._read_repository.list_messages(
            query.chat_id,
            query.user_id,
            limit=query.limit,
            before=query.before,
        )
