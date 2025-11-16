from common.application.exceptions import NotFoundError

from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
    GetChatQuery,
    IGetChatUseCase,
)


class GetChatUseCase(IGetChatUseCase):
    def __init__(
        self,
        chat_read_repository: IChatReadRepository,
    ) -> None:
        self.chat_read_repository = chat_read_repository

    async def execute(self, query: GetChatQuery) -> ChatDTO:
        chat_dto = await self.chat_read_repository.get_by_id_for_user(
            query.chat_id,
            query.user_id,
        )

        if chat_dto is None:
            raise NotFoundError(str(query.chat_id))

        return chat_dto
