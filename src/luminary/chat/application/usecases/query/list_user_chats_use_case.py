"""List user chats query use case implementation."""

from collections.abc import Sequence

from luminary.chat.application.dtos.read_models import ChatSummaryReadModel
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.list_user_chats_use_case import (
    IListUserChatsUseCase,
    ListUserChatsQuery,
)


class ListUserChatsUseCase(IListUserChatsUseCase):
    def __init__(self, read_repository: IChatReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(
        self, query: ListUserChatsQuery
    ) -> Sequence[ChatSummaryReadModel]:
        return await self._read_repository.list_standalone_by_owner(query.user_id)
