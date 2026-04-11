from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import get_descriptor

from luminary.chat.application.interfaces.usecases.command.add_source_to_chat_use_case import (
    AddSourceToChatCommand,
    IAddSourceToChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.cancel_message_use_case import (
    CancelMessageCommand,
    ICancelMessageUseCase,
)
from luminary.chat.application.interfaces.usecases.command.change_chat_assistant_use_case import (
    ChangeChatAssistantCommand,
    IChangeChatAssistantUseCase,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.delete_chat_use_case import (
    DeleteChatCommand,
    IDeleteChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    GetMessageResponseCommand,
    IGetStreamingMessageResponseUseCase,
)
from luminary.chat.application.interfaces.usecases.command.remove_chat_assistant_use_case import (
    IRemoveChatAssistantUseCase,
    RemoveChatAssistantCommand,
)
from luminary.chat.application.interfaces.usecases.command.remove_source_from_chat_use_case import (
    IRemoveSourceFromChatUseCase,
    RemoveSourceFromChatCommand,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
    SendMessageCommand,
)
from luminary.chat.application.interfaces.usecases.command.update_chat_name_use_case import (
    IUpdateChatNameUseCase,
    UpdateChatNameCommand,
)
from luminary.chat.application.interfaces.usecases.command.update_chat_settings_use_case import (
    IUpdateChatSettingsUseCase,
    UpdateChatSettingsCommand,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatByIdQuery,
    IGetChatByIdUseCase,
)
from luminary.chat.application.interfaces.usecases.query.list_chat_messages_use_case import (
    IListChatMessagesUseCase,
    ListChatMessagesQuery,
)
from luminary.chat.application.interfaces.usecases.query.list_user_chats_use_case import (
    IListUserChatsUseCase,
    ListUserChatsQuery,
)
from luminary.chat.presentation.http.dto.request import (
    AddSourceToChatRequest,
    ChangeChatAssistantRequest,
    CreateChatRequest,
    SendMessageRequest,
    UpdateChatNameRequest,
    UpdateChatSettingsRequest,
)
from luminary.chat.presentation.http.dto.response import (
    ChatResponse,
    ChatSummaryResponse,
    MessageResponse,
    StreamingMessageResponse,
)


command_router = APIRouter()


@cbv(command_router)
class ChatCommandController:
    create_chat_use_case: ICreateChatUseCase = Depends()
    update_chat_name_use_case: IUpdateChatNameUseCase = Depends()
    update_chat_settings_use_case: IUpdateChatSettingsUseCase = Depends()
    change_chat_assistant_use_case: IChangeChatAssistantUseCase = Depends()
    remove_chat_assistant_use_case: IRemoveChatAssistantUseCase = Depends()
    add_source_to_chat_use_case: IAddSourceToChatUseCase = Depends()
    remove_source_from_chat_use_case: IRemoveSourceFromChatUseCase = Depends()
    delete_chat_use_case: IDeleteChatUseCase = Depends()
    send_message_use_case: ISendMessageUseCase = Depends()
    get_message_response_use_case: IGetStreamingMessageResponseUseCase = Depends()
    cancel_message_use_case: ICancelMessageUseCase = Depends()

    @command_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        self,
        request: CreateChatRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        chat_id = await self.create_chat_use_case.execute(
            CreateChatCommand(
                user_id=descriptor.identity_id,
                folder_id=None,
                name=request.name,
                assistant_id=request.assistant_id,
                model_id=request.model_id,
                max_context_messages=request.max_context_messages,
            )
        )
        return IDResponse(id=chat_id)

    @command_router.put(
        "/{chat_id:uuid}/name",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_name(
        self,
        chat_id: UUID,
        request: UpdateChatNameRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_chat_name_use_case.execute(
            UpdateChatNameCommand(
                user_id=descriptor.identity_id, chat_id=chat_id, name=request.name
            )
        )

    @command_router.put(
        "/{chat_id:uuid}/settings",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_settings(
        self,
        chat_id: UUID,
        request: UpdateChatSettingsRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_chat_settings_use_case.execute(
            UpdateChatSettingsCommand(
                user_id=descriptor.identity_id,
                chat_id=chat_id,
                model_id=request.model_id,
                max_context_messages=request.max_context_messages,
            )
        )

    @command_router.put(
        "/{chat_id:uuid}/assistant",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def change_assistant(
        self,
        chat_id: UUID,
        request: ChangeChatAssistantRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.change_chat_assistant_use_case.execute(
            ChangeChatAssistantCommand(
                user_id=descriptor.identity_id,
                chat_id=chat_id,
                assistant_id=request.assistant_id,
            )
        )

    @command_router.delete(
        "/{chat_id:uuid}/assistant",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def remove_assistant(
        self,
        chat_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.remove_chat_assistant_use_case.execute(
            RemoveChatAssistantCommand(user_id=descriptor.identity_id, chat_id=chat_id)
        )

    @command_router.post(
        "/{chat_id:uuid}/sources",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def add_source(
        self,
        chat_id: UUID,
        request: AddSourceToChatRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.add_source_to_chat_use_case.execute(
            AddSourceToChatCommand(
                user_id=descriptor.identity_id,
                chat_id=chat_id,
                source_id=request.source_id,
            )
        )

    @command_router.delete(
        "/{chat_id:uuid}/sources/{source_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def remove_source(
        self,
        chat_id: UUID,
        source_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.remove_source_from_chat_use_case.execute(
            RemoveSourceFromChatCommand(
                user_id=descriptor.identity_id, chat_id=chat_id, source_id=source_id
            )
        )

    @command_router.delete(
        "/{chat_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete(
        self,
        chat_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.delete_chat_use_case.execute(
            DeleteChatCommand(user_id=descriptor.identity_id, chat_id=chat_id)
        )

    @command_router.post(
        "/{chat_id:uuid}/messages",
        status_code=status.HTTP_201_CREATED,
    )
    async def send_message(
        self,
        chat_id: UUID,
        request: SendMessageRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        result = await self.send_message_use_case.execute(
            SendMessageCommand(
                user_id=descriptor.identity_id, chat_id=chat_id, content=request.content
            )
        )
        return IDResponse.from_uuid(result)

    @command_router.post("/{chat_id:uuid}/messages/{message_id:uuid}/response")
    async def get_response(
        self,
        chat_id: UUID,
        message_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> StreamingResponse:
        stream = self.get_message_response_use_case.execute(
            GetMessageResponseCommand(
                descriptor.identity_id, chat_id=chat_id, message_id=message_id
            )
        )

        async def process_stream() -> AsyncGenerator[str]:
            async for chunk in stream:
                yield f"data: {StreamingMessageResponse.from_dto(chunk).model_dump_json()}\n\n"

        return StreamingResponse(process_stream(), media_type="text/event-stream")

    @command_router.post(
        "/{chat_id:uuid}/messages/{message_id:uuid}/cancel",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def cancel_message(
        self,
        chat_id: UUID,
        message_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.cancel_message_use_case.execute(
            CancelMessageCommand(
                user_id=descriptor.identity_id, chat_id=chat_id, message_id=message_id
            )
        )


query_router = APIRouter()


@cbv(query_router)
class ChatQueryController:
    get_chat_by_id_use_case: IGetChatByIdUseCase = Depends()
    list_user_chats_use_case: IListUserChatsUseCase = Depends()
    list_chat_messages_use_case: IListChatMessagesUseCase = Depends()

    @query_router.get("/{chat_id:uuid}/messages")
    async def list_messages(
        self,
        chat_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
        limit: int = 50,
        before: UUID | None = None,
    ) -> list[MessageResponse]:
        read_models = await self.list_chat_messages_use_case.execute(
            ListChatMessagesQuery(
                user_id=descriptor.identity_id,
                chat_id=chat_id,
                limit=limit,
                before=before,
            )
        )
        return [MessageResponse.from_read_model(m) for m in read_models]

    @query_router.get("/{chat_id:uuid}")
    async def get_chat(
        self,
        chat_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> ChatResponse:
        read_model = await self.get_chat_by_id_use_case.execute(
            GetChatByIdQuery(user_id=descriptor.identity_id, chat_id=chat_id)
        )
        return ChatResponse.from_read_model(read_model)

    @query_router.get("/")
    async def list_chats(
        self,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> list[ChatSummaryResponse]:
        read_models = await self.list_user_chats_use_case.execute(
            ListUserChatsQuery(user_id=descriptor.identity_id)
        )
        return [ChatSummaryResponse.from_read_model(m) for m in read_models]
