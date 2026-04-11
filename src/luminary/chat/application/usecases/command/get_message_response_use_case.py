from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass

from common.application.exceptions import NotFoundError
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.repositories.message_reader import (
    IMessageReader,
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
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.model.application.interfaces.services.engine import (
    IInferenceEngine,
    InferenceRequestDTO,
    MessageDTO,
    Role,
)


def _author_to_role(author: Author) -> Role:
    if author == Author.USER:
        return Role.USER
    if author == Author.ASSISTANT:
        return Role.ASSISTANT
    return Role.SYSTEM


def _messages_to_history(messages: Sequence[Message]) -> Sequence[MessageDTO]:
    return [
        MessageDTO(content=msg.content, role=_author_to_role(msg.role))
        for msg in messages
    ]


def _stream_dto(
    response: Message, state: StreamState, content: str
) -> StreamingMessageDTO:
    return StreamingMessageDTO(
        state=state,
        content=content,
        message_id=response.id.value,
        author=response.role,
        status=response.status,
    )


@dataclass(frozen=True)
class _ResolvedContext:
    chat: Chat
    messages: Sequence[Message]
    request: Message
    folder: Folder | None


class GetStreamingMessageResponseUseCase(IGetStreamingMessageResponseUseCase):
    DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

    def __init__(  # noqa: PLR0913
        self,
        uow: IUnitOfWork,
        message_factory: IMessageFactory,
        inference_engine: IInferenceEngine,
        chat_repository: IChatRepository,
        assistant_repository: IAssistantRepository,
        folder_repository: IFolderRepository,
        message_reader: IMessageReader,
        message_repository: IMessageRepository,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.uow = uow
        self.message_factory = message_factory
        self.inference_engine = inference_engine
        self.chat_repository = chat_repository
        self.assistant_repository = assistant_repository
        self.folder_repository = folder_repository
        self.message_reader = message_reader
        self.message_repository = message_repository
        self.chat_access_policy = chat_access_policy

    async def execute(
        self, command: GetMessageResponseCommand
    ) -> AsyncGenerator[StreamingMessageDTO]:
        ctx = await self._load_context(command)

        response = self.message_factory.create(
            MessageFactoryDTO(
                chat_id=ctx.chat.id,
                model_id=ctx.chat.settings.model_id,
                role=Author.ASSISTANT,
                content=EMPTY_CONTENT,
            )
        )
        response.start_streaming()

        yield _stream_dto(response, StreamState.START, STREAM_START_CONTENT)

        history = _messages_to_history(ctx.messages[:-1])
        if ctx.folder is not None:
            source_ids = list(
                {sid.value for sid in ctx.chat.sources}
                | {sid.value for sid in ctx.folder.sources}
            )
        else:
            source_ids = [sid.value for sid in ctx.chat.sources]

        system_prompt = await self._get_system_prompt(ctx)
        editor_content: str | None = None
        if ctx.folder is not None and ctx.folder.editor_content is not None:
            editor_content = ctx.folder.editor_content.text

        request = InferenceRequestDTO(
            query=ctx.request.content,
            system_prompt=system_prompt,
            source_ids=source_ids,
            history=history,
            editor_content=editor_content,
        )
        async for chunk in self.inference_engine.send(request):
            response.add_chunk(chunk.content)
            yield _stream_dto(response, StreamState.DELTA, chunk.content)

        ctx.request.complete(0)
        response.complete(0)

        async with self.uow:
            await self.message_repository.save(ctx.request)
            await self.message_repository.add(response)

        yield _stream_dto(response, StreamState.END, STREAM_END_CONTENT)

    async def _load_context(
        self, command: GetMessageResponseCommand
    ) -> _ResolvedContext:
        user_id = UserId(command.user_id)
        chat_id = ChatId(command.chat_id)
        message_id = MessageId(command.message_id)

        chat = await self.chat_repository.get_by_id(chat_id)
        self.chat_access_policy.assert_is_allowed(user_id, chat)

        messages = await self.message_reader.get_chat_messages(
            chat_id, limit=chat.settings.max_context_messages
        )
        if not messages:
            raise InvariantViolationError(
                "At least one user message is required for generating response"
            )

        request = messages[-1]
        if request.id != message_id:
            raise NotFoundError(message_id)

        folder: Folder | None = None
        if chat.folder_id is not None:
            folder = await self.folder_repository.get_by_id(chat.folder_id)

        return _ResolvedContext(
            chat=chat, messages=messages, request=request, folder=folder
        )

    async def _get_system_prompt(self, ctx: _ResolvedContext) -> str:
        if ctx.chat.assistant_id is not None:
            assistant = await self.assistant_repository.get_by_id(ctx.chat.assistant_id)
            return assistant.instructions.prompt
        if ctx.folder is not None and ctx.folder.assistant_id is not None:
            assistant = await self.assistant_repository.get_by_id(
                ctx.folder.assistant_id
            )
            return assistant.instructions.prompt
        return self.DEFAULT_SYSTEM_PROMPT
