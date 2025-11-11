from common.application.exceptions import NotFoundError

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
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
        chat_repository: IChatRepository,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.chat_read_repository = chat_read_repository
        self.chat_repository = chat_repository
        self.chat_access_policy = chat_access_policy

    async def execute(self, query: GetChatQuery) -> ChatDTO:

        chat_entity = await self.chat_repository.get_by_id(query.chat_id)

        self.chat_access_policy.assert_is_allowed(query.user_id, chat_entity)

        chat_dto = await self.chat_read_repository.get_by_id(query.chat_id)

        if chat_dto is None:
            raise NotFoundError(query.chat_id)

        return chat_dto
