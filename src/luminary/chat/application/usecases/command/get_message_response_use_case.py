from collections.abc import AsyncGenerator

from common.application.exceptions import NotFoundError
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_repository import (
    IMessageRepository,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    GetMessageResponseCommand,
    IGetStreamingMessageResponseUseCase,
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.domain.enums import Author
from luminary.chat.domain.interfaces.message_factory import IMessageFactory
from luminary.model.application.interfaces.services.ai_provider import AIProvider


class GetStreamingMessageResponseUseCase(IGetStreamingMessageResponseUseCase):
    def __init__(
        self,
        message_factory: IMessageFactory,
        uow: IUnitOfWork,
        ai_provider: AIProvider,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
    ) -> None:
        self.message_factory = message_factory
        self.uow = uow
        self.ai_provider = ai_provider
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    async def execute(
        self, command: GetMessageResponseCommand
    ) -> AsyncGenerator[StreamingMessageDTO]:
        chat = await self.chat_repository.get_by_id(command.chat_id)
        request = await self.message_repository.get_by_id(command.message_id)
        if chat.chat_id != request.message_id:
            raise NotFoundError(request.message_id)

        # TODO: Policy

        response = self.message_factory.create(
            chat_id=chat.chat_id,
            model_id=chat.settings.model_id,
            role=Author.ASSISTANT,
            content="Placeholder",
        )
        response.start_streaming()

        messages = [request.content]

        yield StreamingMessageDTO(
            state=StreamState.START,
            content="start",
            message_id=response.message_id,
            author=response.role,
            status=response.status,
        )

        request_tokens = 0
        response_tokens = 0  # TODO: How and when assign tokens
        async for chunk in self.ai_provider.stream_completion(
            messages, chat.settings.system_prompt, chat.settings.model_id
        ):
            response.add_chunk(chunk.content)

            yield StreamingMessageDTO(
                state=StreamState.DELTA,
                content=chunk.content,
                message_id=response.message_id,
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
            content="end",
            message_id=response.message_id,
            author=response.role,
            status=response.status,
        )
