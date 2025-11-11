from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.auth import get_descriptor, require_authenticated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv

from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    GetMessageResponseCommand,
    IGetStreamingMessageResponseUseCase,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
    SendMessageCommand,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatQuery,
    IGetChatUseCase,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    GetUserChatsQuery,
    IGetUserChatsUseCase,
)
from luminary.chat.presentation.http.dto.request import SendMessageRequest
from luminary.chat.presentation.http.dto.response import (
    ChatListItemResponse,
    ChatResponse,
    MessageResponse,
    StreamingMessageResponse,
)


chat_command_router = APIRouter()
chat_query_router = APIRouter()


@cbv(chat_command_router)
class ChatCommandController:
    create_chat_use_case: ICreateChatUseCase = Depends()
    send_message_use_case: ISendMessageUseCase = Depends()
    get_message_response_use_case: IGetStreamingMessageResponseUseCase = Depends()

    @chat_command_router.post("/", dependencies=[Depends(require_authenticated)])
    async def create(
        self, descriptor: Annotated[UUID, Depends(get_descriptor)]
    ) -> IDResponse:
        chat_id = await self.create_chat_use_case.execute(
            CreateChatCommand(descriptor, assistant_id=None)
        )
        return IDResponse(id=chat_id)

    @chat_command_router.post(
        "/{chat_id}", dependencies=[Depends(require_authenticated)]
    )
    async def send_message(
        self,
        chat_id: UUID,
        request: SendMessageRequest,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> MessageResponse:
        message = await self.send_message_use_case.execute(
            SendMessageCommand(descriptor, chat_id, request.message)
        )
        return MessageResponse.from_dto(message)

    @chat_command_router.post(
        "/{chat_id}/{message_id}", dependencies=[Depends(require_authenticated)]
    )
    async def get_response(
        self,
        chat_id: UUID,
        message_id: UUID,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> StreamingResponse:
        stream = self.get_message_response_use_case.execute(
            GetMessageResponseCommand(
                descriptor, chat_id=chat_id, message_id=message_id
            )
        )

        async def process_stream() -> AsyncGenerator[str]:
            async for chunk in stream:
                yield StreamingMessageResponse.from_dto(chunk).model_dump_json()

        # TODO: Error handling
        return StreamingResponse(process_stream())


@cbv(chat_query_router)
class ChatQueryController:
    get_chat_use_case: IGetChatUseCase = Depends()
    get_user_chats_use_case: IGetUserChatsUseCase = Depends()

    @chat_query_router.get(
        "/{chat_id}",
        dependencies=[Depends(require_authenticated)],
        summary="Получить чат по ID",
        description="Возвращает полную информацию o чате. Требует права доступа к чату.",
    )
    async def get_chat(
        self,
        chat_id: UUID,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> ChatResponse:
        dto = await self.get_chat_use_case.execute(
            GetChatQuery(user_id=descriptor, chat_id=chat_id)
        )
        return ChatResponse.from_dto(dto)

    @chat_query_router.get(
        "/",
        dependencies=[Depends(require_authenticated)],
        summary="Получить список чатов пользователя",
        description="Возвращает список чатов. Опционально можно фильтровать по папке.",
    )
    async def get_user_chats(
        self,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
        folder_id: UUID | None = None,
    ) -> list[ChatListItemResponse]:
        dtos = await self.get_user_chats_use_case.execute(
            GetUserChatsQuery(user_id=descriptor, folder_id=folder_id)
        )
        return [ChatListItemResponse.from_dto(dto) for dto in dtos]
