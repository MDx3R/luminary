from collections.abc import Sequence

from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
    GetUserChatsQuery,
    IGetUserChatsUseCase,
)


class GetUserChatsUseCase(IGetUserChatsUseCase):

    def __init__(self, chat_read_repository: IChatReadRepository) -> None:

        self.chat_read_repository = chat_read_repository

    async def execute(self, query: GetUserChatsQuery) -> Sequence[ChatListItemDTO]:
        if query.folder_id is not None:
            return await self.chat_read_repository.get_by_folder_id(query.folder_id)

        return await self.chat_read_repository.get_by_user_id(query.user_id)
