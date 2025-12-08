from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
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
    MessageDTO,
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
        message_factory: IMessageFactory,
        uow: IUnitOfWork,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.message_factory = message_factory
        self.uow = uow
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.chat_access_policy = chat_access_policy

    async def execute(self, command: SendMessageCommand) -> MessageDTO:
        chat_id = ChatId(command.chat_id)

        chat = await self.chat_repository.get_by_id(chat_id)

        self.chat_access_policy.assert_is_allowed(UserId(command.user_id), chat)

        message = self.message_factory.create(
            MessageFactoryDTO(
                chat_id=chat_id,
                model_id=chat.settings.model_id,
                role=Author.USER,
                content=command.message,
            )
        )

        await self.message_repository.add(message)

        return MessageDTO(
            message_id=message.id.value,
            chat_id=message.chat_id.value,
            author=message.role,
            status=message.status,
            content=message.content,
            tokens=None,
            created_at=message.created_at,
        )
