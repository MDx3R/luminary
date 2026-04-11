from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.cancel_message_use_case import (
    CancelMessageCommand,
    ICancelMessageUseCase,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId


class CancelMessageUseCase(ICancelMessageUseCase):
    def __init__(
        self,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        access_policy: IChatAccessPolicy,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.access_policy = access_policy

    async def execute(self, command: CancelMessageCommand) -> None:
        chat_id = ChatId(command.chat_id)
        chat = await self.chat_repository.get_by_id(chat_id)
        self.access_policy.assert_is_allowed(UserId(command.user_id), chat)

        message = await self.message_repository.get_by_id(MessageId(command.message_id))
        if message.chat_id != chat_id:
            raise ValueError("Message does not belong to this chat")

        message.cancel()
        await self.message_repository.save(message)
