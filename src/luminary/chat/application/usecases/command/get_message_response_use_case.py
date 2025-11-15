from collections.abc import AsyncGenerator

from common.application.exceptions import NotFoundError
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
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    EMPTY_CONTENT,
    STREAM_END_CONTENT,
    STREAM_START_CONTENT,
    GetMessageResponseCommand,
    IGetStreamingMessageResponseUseCase,
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.domain.enums import Author
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.model.application.interfaces.services.ai_provider import AIProvider


class GetStreamingMessageResponseUseCase(IGetStreamingMessageResponseUseCase):
    def __init__(  # noqa: PLR0913
        self,
        message_factory: IMessageFactory,
        uow: IUnitOfWork,
        ai_provider: AIProvider,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.message_factory = message_factory
        self.uow = uow
        self.ai_provider = ai_provider
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.chat_access_policy = chat_access_policy

    async def execute(
        self, command: GetMessageResponseCommand
    ) -> AsyncGenerator[StreamingMessageDTO]:
        user_id = UserId(command.user_id)
        chat_id = ChatId(command.chat_id)

        chat = await self.chat_repository.get_by_id(chat_id)
        request = await self.message_repository.get_by_id(command.message_id)
        if chat.id != request.chat_id:
            raise NotFoundError(request.id)

        self.chat_access_policy.assert_is_allowed(user_id, chat)

        response = self.message_factory.create(
            MessageFactoryDTO(
                chat_id=chat_id,
                model_id=chat.settings.model_id,
                role=Author.ASSISTANT,
                content=EMPTY_CONTENT,
            )
        )
        response.start_streaming()

        messages = [request.content]
        response_id = response.id.value

        yield StreamingMessageDTO(
            state=StreamState.START,
            content=STREAM_START_CONTENT,
            message_id=response_id,
            author=response.role,
            status=response.status,
        )

        request_tokens = 0
        response_tokens = 0  # TODO: How and when assign tokens
        async for chunk in self.ai_provider.stream_completion(
            messages, chat.settings.system_prompt, chat.settings.model_id.value
        ):
            response.add_chunk(chunk.content)

            yield StreamingMessageDTO(
                state=StreamState.DELTA,
                content=chunk.content,
                message_id=response_id,
                author=response.role,
                status=response.status,
            )

        request.complete(request_tokens)
        response.complete(response_tokens)

        async with self.uow:
            await self.message_repository.save(request)
            await self.message_repository.add(response)

        yield StreamingMessageDTO(
            state=StreamState.END,
            content=STREAM_END_CONTENT,
            message_id=response_id,
            author=response.role,
            status=response.status,
        )
