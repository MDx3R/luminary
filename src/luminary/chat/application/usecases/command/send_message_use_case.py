from uuid import UUID

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
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
    SendMessageCommand,
)
from luminary.chat.domain.enums import Author
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)
from luminary.chat.domain.value_objects.chat_id import ChatId


class SendMessageUseCase(ISendMessageUseCase):
    def __init__(
        self,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        message_factory: IMessageFactory,
        access_policy: IChatAccessPolicy,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.message_factory = message_factory
        self.access_policy = access_policy

    async def execute(self, command: SendMessageCommand) -> UUID:
        user_id = UserId(command.user_id)
        chat_id = ChatId(command.chat_id)

        chat = await self.chat_repository.get_by_id(chat_id)
        self.access_policy.assert_is_allowed(user_id, chat)

        message = self.message_factory.create(
            MessageFactoryDTO(
                chat_id=chat_id,
                model_id=chat.settings.model_id,
                role=Author.USER,
                content=command.content,
            )
        )

        await self.message_repository.add(message)

        return message.id.value
