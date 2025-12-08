from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.add_source_to_chat_use_case import (
    AddSourceToChatCommand,
    IAddSourceToChatUseCase,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import SourceId


class AddSourceToChatUseCase(IAddSourceToChatUseCase):
    def __init__(
        self,
        chat_access_policy: IChatAccessPolicy,
        chat_repository: IChatRepository,
        source_access_policy: ISourceAccessPolicy,
        source_repository: ISourceRepository,
    ) -> None:
        self.chat_access_policy = chat_access_policy
        self.chat_repository = chat_repository
        self.source_access_policy = source_access_policy
        self.source_repository = source_repository

    async def execute(self, command: AddSourceToChatCommand) -> None:
        user_id = UserId(command.user_id)
        source_id = SourceId(command.source_id)

        chat = await self.chat_repository.get_by_id(ChatId(command.chat_id))
        self.chat_access_policy.assert_is_allowed(user_id, chat)

        if chat.has_source(source_id):
            return

        source = await self.source_repository.get_by_id(source_id)
        self.source_access_policy.assert_is_allowed(user_id, source)

        chat.add_source(source_id)

        await self.chat_repository.save(chat)
