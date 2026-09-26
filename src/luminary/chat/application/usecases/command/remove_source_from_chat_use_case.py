from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.remove_source_from_chat_use_case import (
    IRemoveSourceFromChatUseCase,
    RemoveSourceFromChatCommand,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.source.domain.entity.source import SourceId


class RemoveSourceFromChatUseCase(IRemoveSourceFromChatUseCase):
    def __init__(
        self,
        repository: IChatRepository,
        access_policy: IChatAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: RemoveSourceFromChatCommand) -> None:
        chat = await self.repository.get_by_id(ChatId(command.chat_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), chat)

        if not chat.has_source(SourceId(command.source_id)):
            return

        chat.remove_source(SourceId(command.source_id))
        await self.repository.save(chat)
