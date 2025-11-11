from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    MessageDTO,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
)
from luminary.chat.domain.enums import Author, MessageStatus


class MessageResponse(BaseModel):
    message_id: UUID
    chat_id: UUID
    content: str
    author: Author
    status: MessageStatus
    tokens: int | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: MessageDTO) -> Self:
        return cls(
            message_id=dto.message_id,
            chat_id=dto.chat_id,
            content=dto.content,
            author=dto.author,
            status=dto.status,
            tokens=dto.tokens,
            created_at=dto.created_at.value,
        )


class StreamingMessageResponse(BaseModel):
    message_id: UUID
    state: StreamState
    content: str
    author: Author
    status: MessageStatus

    @classmethod
    def from_dto(cls, dto: StreamingMessageDTO) -> Self:
        return cls(
            message_id=dto.message_id,
            state=dto.state,
            content=dto.content,
            author=dto.author,
            status=dto.status,
        )


class ChatResponse(BaseModel):
    chat_id: UUID
    user_id: UUID
    folder_id: UUID | None
    name: str
    model_id: UUID
    system_prompt: str
    max_context_messages: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: ChatDTO) -> Self:
        return cls(
            chat_id=dto.chat_id,
            user_id=dto.user_id,
            folder_id=dto.folder_id,
            name=dto.name,
            model_id=dto.model_id,
            system_prompt=dto.system_prompt,
            max_context_messages=dto.max_context_messages,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class ChatListItemResponse(BaseModel):
    chat_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: ChatListItemDTO) -> Self:
        return cls(
            chat_id=dto.chat_id,
            name=dto.name,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
