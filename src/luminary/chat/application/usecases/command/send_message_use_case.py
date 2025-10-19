from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

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
from luminary.chat.domain.interfaces.message_factory import IMessageFactory


class SendMessageUseCase(ISendMessageUseCase):
    def __init__(
        self,
        message_factory: IMessageFactory,
        uow: IUnitOfWork,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
    ) -> None:
        self.message_factory = message_factory
        self.uow = uow
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    async def execute(self, command: SendMessageCommand) -> MessageDTO:
        chat = await self.chat_repository.get_by_id(command.chat_id)

        message = self.message_factory.create(
            chat.chat_id, chat.settings.model_id, Author.USER, command.message
        )
        message.start_processing()

        await self.message_repository.add(message)

        # TODO: Send prompt
        try:
            response_content = "123"
            request_tokens, response_tokens = 10, 10
            response = self.message_factory.create(
                chat.chat_id, chat.settings.model_id, Author.ASSISTANT, response_content
            )
        except Exception:
            message.fail()
            await self.message_repository.save(message)
            return MessageDTO(
                message_id=message.message_id,
                chat_id=message.chat_id,
                author=message.role,
                status=message.status,
                content=message.content,
                tokens=None,
                created_at=message.created_at,
                response=None,
            )

        message.complete(request_tokens)

        async with self.uow:
            await self.message_repository.save(message)
            await self.message_repository.save(response)

        response_dto = MessageDTO(
            message_id=response.message_id,
            chat_id=response.chat_id,
            author=response.role,
            status=response.status,
            content=response.content,
            tokens=response_tokens,
            created_at=response.created_at,
            response=None,
        )
        return MessageDTO(
            message_id=message.message_id,
            chat_id=message.chat_id,
            author=message.role,
            status=message.status,
            content=message.content,
            tokens=request_tokens,
            created_at=message.created_at,
            response=response_dto,
        )
